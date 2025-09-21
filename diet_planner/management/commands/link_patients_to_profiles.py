from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diet_planner.models import Patient
from user_management.models import UserProfile, PatientProfile


class Command(BaseCommand):
    help = 'Link existing patients to user profiles or create user profiles for them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all patients without user profiles
        patients_without_profiles = Patient.objects.filter(user_profile__isnull=True)
        
        self.stdout.write(f'Found {patients_without_profiles.count()} patients without user profiles')
        
        created_count = 0
        linked_count = 0
        error_count = 0
        
        for patient in patients_without_profiles:
            try:
                # Generate a unique email for the patient
                email = f"patient_{patient.id}@nk360.com"
                
                # Check if user already exists with this email
                try:
                    user = User.objects.get(email=email)
                    user_profile = UserProfile.objects.get(user=user)
                    self.stdout.write(f'Found existing user profile for {patient.name} ({email})')
                except (User.DoesNotExist, UserProfile.DoesNotExist):
                    if not dry_run:
                        # Create new user and profile
                        user = User.objects.create_user(
                            username=f"patient_{patient.id}",
                            email=email,
                            first_name=patient.name.split()[0] if patient.name else "Patient",
                            last_name=patient.name.split()[-1] if patient.name and len(patient.name.split()) > 1 else "",
                            password="temp_password_123"  # Temporary password
                        )
                        user_profile = UserProfile.objects.create(
                            user=user,
                            user_type='patient',
                            phone_number=""
                        )
                        PatientProfile.objects.create(user_profile=user_profile)
                        self.stdout.write(f'Created user profile for {patient.name} ({email})')
                    else:
                        self.stdout.write(f'Would create user profile for {patient.name} ({email})')
                    created_count += 1
                
                if not dry_run:
                    # Link patient to user profile
                    patient.user_profile = user_profile
                    patient.save()
                    linked_count += 1
                    self.stdout.write(f'Linked {patient.name} to user profile')
                else:
                    self.stdout.write(f'Would link {patient.name} to user profile')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error processing {patient.name}: {str(e)}')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would create {created_count} user profiles and link {linked_count} patients')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} user profiles and linked {linked_count} patients')
            )
            
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Encountered {error_count} errors')
            )
