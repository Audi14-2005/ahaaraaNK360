from django.core.management.base import BaseCommand
from medical_ocr.models import MedicalDocument
from medical_ocr.services import MedicalDocumentProcessor
import os

class Command(BaseCommand):
    help = 'Check document status and test processing'

    def handle(self, *args, **options):
        self.stdout.write("📋 Checking Document Status")
        self.stdout.write("=" * 50)
        
        documents = MedicalDocument.objects.all()
        self.stdout.write(f"Total documents: {documents.count()}")
        
        for doc in documents:
            self.stdout.write(f"\n📄 Document: {doc.patient_name} (ID: {doc.patient_id})")
            self.stdout.write(f"   Status: {doc.status}")
            self.stdout.write(f"   Type: {doc.document_type}")
            self.stdout.write(f"   Uploaded: {doc.uploaded_at}")
            self.stdout.write(f"   Processed: {doc.processed_at}")
            self.stdout.write(f"   File: {doc.document_file}")
            self.stdout.write(f"   Extracted Text Length: {len(doc.extracted_text) if doc.extracted_text else 0}")
            self.stdout.write(f"   AI Summary Length: {len(doc.ai_summary) if doc.ai_summary else 0}")
            
            if doc.status == 'failed':
                self.stdout.write(f"   ❌ Error: {doc.error_message}")
            elif doc.status == 'uploaded':
                self.stdout.write(f"   ⏳ Ready for processing")
            elif doc.status == 'processing':
                self.stdout.write(f"   🔄 Currently processing")
            elif doc.status == 'completed':
                self.stdout.write(f"   ✅ Successfully processed")

        # Test processing
        self.stdout.write("\n🧪 Testing Document Processing")
        self.stdout.write("=" * 50)
        
        test_doc = MedicalDocument.objects.filter(status='uploaded').first()
        if not test_doc:
            test_doc = MedicalDocument.objects.filter(status='failed').first()
        
        if not test_doc:
            self.stdout.write("❌ No documents found to test")
            return
        
        self.stdout.write(f"Testing with document: {test_doc.patient_name}")
        self.stdout.write(f"File path: {test_doc.document_file.path}")
        
        if not os.path.exists(test_doc.document_file.path):
            self.stdout.write(f"❌ File not found: {test_doc.document_file.path}")
            return
        
        self.stdout.write(f"✅ File exists, size: {os.path.getsize(test_doc.document_file.path)} bytes")
        
        try:
            processor = MedicalDocumentProcessor()
            self.stdout.write("✅ Processor initialized")
            
            self.stdout.write("🔍 Testing OCR...")
            ocr_result = processor.process_document(test_doc.document_file.path)
            self.stdout.write(f"✅ OCR completed, extracted {len(ocr_result.get('text', ''))} characters")
            
            self.stdout.write("🤖 Testing AI summarization...")
            ai_result = processor.generate_ai_summary(ocr_result.get('text', ''))
            self.stdout.write(f"✅ AI summarization completed")
            
            self.stdout.write("\n🎉 Processing test successful!")
            
        except Exception as e:
            self.stdout.write(f"❌ Processing test failed: {e}")
            import traceback
            traceback.print_exc()


