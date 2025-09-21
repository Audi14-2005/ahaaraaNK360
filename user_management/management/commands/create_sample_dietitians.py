from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_management.models import UserProfile, DietitianProfile


class Command(BaseCommand):
    help = 'Create sample dietitians for testing'

    def handle(self, *args, **options):
        # Create sample dietitians
        dietitians_data = [
            {
                'username': 'dr_sarah',
                'first_name': 'Dr. Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@nk360.com',
                'password': 'password123',
                'specialization': 'Certified Ayurvedic Practitioner'
            },
            {
                'username': 'dr_michael',
                'first_name': 'Dr. Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@nk360.com',
                'password': 'password123',
                'specialization': 'Registered Dietitian & Nutritionist'
            },
            {
                'username': 'dr_priya',
                'first_name': 'Dr. Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@nk360.com',
                'password': 'password123',
                'specialization': 'Ayurvedic Medicine Specialist'
            }
        ]
        
        for dietitian_data in dietitians_data:
            # Check if user already exists
            if User.objects.filter(username=dietitian_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Dietitian {dietitian_data["username"]} already exists')
                )
                continue
            
            # Create user
            user = User.objects.create_user(
                username=dietitian_data['username'],
                first_name=dietitian_data['first_name'],
                last_name=dietitian_data['last_name'],
                email=dietitian_data['email'],
                password=dietitian_data['password']
            )
            
            # Create user profile
            user_profile = UserProfile.objects.create(
                user=user,
                user_type='dietitian',
                phone_number='+1-555-0123',
                is_verified=True
            )
            
            # Create dietitian profile
            dietitian_profile = DietitianProfile.objects.create(
                user_profile=user_profile,
                specialization=dietitian_data['specialization'],
                license_number=f'LIC-{dietitian_data["username"].upper()}',
                experience_years=5,
                bio=f"Experienced {dietitian_data['specialization']} with 5+ years of practice."
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created dietitian: {user.get_full_name()}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Sample dietitians created successfully!')
        )
