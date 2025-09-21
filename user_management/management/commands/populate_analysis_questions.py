from django.core.management.base import BaseCommand
from user_management.models import PrakritiQuestion, PrakritiOption, DiseaseQuestion


class Command(BaseCommand):
    help = 'Populate Prakriti and Disease analysis questions'

    def handle(self, *args, **options):
        # Prakriti Analysis Questions (20 questions)
        prakriti_questions = [
            {
                'question': 'What is your body frame?',
                'options': [
                    ('Thin and light', 'vata', 1.0),
                    ('Medium and well-proportioned', 'pitta', 1.0),
                    ('Large and heavy', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How is your skin texture?',
                'options': [
                    ('Dry and rough', 'vata', 1.0),
                    ('Smooth and warm', 'pitta', 1.0),
                    ('Thick and oily', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your hair type?',
                'options': [
                    ('Dry, thin, and brittle', 'vata', 1.0),
                    ('Fine, straight, and early graying', 'pitta', 1.0),
                    ('Thick, oily, and wavy', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How are your eyes?',
                'options': [
                    ('Small, dry, and restless', 'vata', 1.0),
                    ('Medium, sharp, and light-sensitive', 'pitta', 1.0),
                    ('Large, attractive, and calm', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your appetite like?',
                'options': [
                    ('Irregular and variable', 'vata', 1.0),
                    ('Strong and regular', 'pitta', 1.0),
                    ('Slow and steady', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you digest food?',
                'options': [
                    ('Irregular, sometimes constipated', 'vata', 1.0),
                    ('Good, sometimes loose stools', 'pitta', 1.0),
                    ('Slow but steady', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your energy level?',
                'options': [
                    ('Bursts of energy, then tired', 'vata', 1.0),
                    ('Moderate and sustained', 'pitta', 1.0),
                    ('Steady and enduring', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you handle stress?',
                'options': [
                    ('Worry and anxiety', 'vata', 1.0),
                    ('Anger and irritability', 'pitta', 1.0),
                    ('Avoidance and withdrawal', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your sleep pattern?',
                'options': [
                    ('Light and interrupted', 'vata', 1.0),
                    ('Moderate and sound', 'pitta', 1.0),
                    ('Deep and heavy', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How is your memory?',
                'options': [
                    ('Quick to learn, quick to forget', 'vata', 1.0),
                    ('Sharp and focused', 'pitta', 1.0),
                    ('Slow to learn, long retention', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your speech pattern?',
                'options': [
                    ('Fast and talkative', 'vata', 1.0),
                    ('Sharp and precise', 'pitta', 1.0),
                    ('Slow and deliberate', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you handle cold weather?',
                'options': [
                    ('Very uncomfortable', 'vata', 1.0),
                    ('Moderately comfortable', 'pitta', 1.0),
                    ('Quite comfortable', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you handle hot weather?',
                'options': [
                    ('Moderately comfortable', 'vata', 1.0),
                    ('Very uncomfortable', 'pitta', 1.0),
                    ('Quite comfortable', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your walking style?',
                'options': [
                    ('Fast and irregular', 'vata', 1.0),
                    ('Moderate and purposeful', 'pitta', 1.0),
                    ('Slow and steady', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How is your joint flexibility?',
                'options': [
                    ('Very flexible', 'vata', 1.0),
                    ('Moderately flexible', 'pitta', 1.0),
                    ('Less flexible', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your emotional nature?',
                'options': [
                    ('Changeable and moody', 'vata', 1.0),
                    ('Intense and passionate', 'pitta', 1.0),
                    ('Calm and stable', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you make decisions?',
                'options': [
                    ('Quickly but changeable', 'vata', 1.0),
                    ('Quickly and decisively', 'pitta', 1.0),
                    ('Slowly but firmly', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your spending pattern?',
                'options': [
                    ('Impulsive and irregular', 'vata', 1.0),
                    ('Moderate and planned', 'pitta', 1.0),
                    ('Conservative and saving', 'kapha', 1.0),
                ]
            },
            {
                'question': 'How do you handle new situations?',
                'options': [
                    ('Enthusiastic but anxious', 'vata', 1.0),
                    ('Confident and direct', 'pitta', 1.0),
                    ('Cautious and methodical', 'kapha', 1.0),
                ]
            },
            {
                'question': 'What is your general temperament?',
                'options': [
                    ('Creative and spontaneous', 'vata', 1.0),
                    ('Ambitious and competitive', 'pitta', 1.0),
                    ('Peaceful and content', 'kapha', 1.0),
                ]
            }
        ]
        
        # Create Prakriti questions
        for i, q_data in enumerate(prakriti_questions, 1):
            question, created = PrakritiQuestion.objects.get_or_create(
                question_number=i,
                defaults={
                    'question_text': q_data['question'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created Prakriti question {i}: {q_data["question"]}')
                
                # Create options for this question
                for option_text, dosha_type, weight in q_data['options']:
                    PrakritiOption.objects.create(
                        question=question,
                        option_text=option_text,
                        dosha_type=dosha_type,
                        weight=weight
                    )
            else:
                self.stdout.write(f'Prakriti question {i} already exists')
        
        # Disease Analysis Questions (15 questions)
        disease_questions = [
            {
                'question': 'Do you have any cardiovascular conditions (heart disease, high blood pressure, etc.)?',
                'category': 'Cardiovascular'
            },
            {
                'question': 'Do you have any respiratory conditions (asthma, COPD, etc.)?',
                'category': 'Respiratory'
            },
            {
                'question': 'Do you have any digestive disorders (IBS, acid reflux, etc.)?',
                'category': 'Digestive'
            },
            {
                'question': 'Do you have diabetes or blood sugar issues?',
                'category': 'Endocrine'
            },
            {
                'question': 'Do you have any joint or bone problems (arthritis, osteoporosis, etc.)?',
                'category': 'Musculoskeletal'
            },
            {
                'question': 'Do you have any neurological conditions (migraines, seizures, etc.)?',
                'category': 'Neurological'
            },
            {
                'question': 'Do you have any skin conditions (eczema, psoriasis, etc.)?',
                'category': 'Dermatological'
            },
            {
                'question': 'Do you have any kidney or urinary tract issues?',
                'category': 'Urological'
            },
            {
                'question': 'Do you have any liver or gallbladder problems?',
                'category': 'Hepatobiliary'
            },
            {
                'question': 'Do you have any thyroid disorders?',
                'category': 'Endocrine'
            },
            {
                'question': 'Do you have any autoimmune conditions?',
                'category': 'Autoimmune'
            },
            {
                'question': 'Do you have any mental health conditions (anxiety, depression, etc.)?',
                'category': 'Mental Health'
            },
            {
                'question': 'Do you have any sleep disorders?',
                'category': 'Sleep'
            },
            {
                'question': 'Do you have any allergies or food intolerances?',
                'category': 'Allergies'
            },
            {
                'question': 'Do you have any chronic pain conditions?',
                'category': 'Pain Management'
            }
        ]
        
        # Create Disease questions
        for i, q_data in enumerate(disease_questions, 1):
            question, created = DiseaseQuestion.objects.get_or_create(
                question_number=i,
                defaults={
                    'question_text': q_data['question'],
                    'category': q_data['category'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created Disease question {i}: {q_data["question"]}')
            else:
                self.stdout.write(f'Disease question {i} already exists')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated all analysis questions!'
            )
        )

