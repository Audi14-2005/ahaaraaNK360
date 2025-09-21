# Medical OCR Analysis System

A comprehensive AI-powered OCR system for analyzing patient reports and prescriptions, designed to provide intelligent summaries for doctors.

## 🏥 Features

### Core Functionality
- **Document Upload**: Support for PDF, PNG, JPG, JPEG, TIFF formats
- **OCR Text Extraction**: Advanced image preprocessing and text recognition
- **AI-Powered Analysis**: Intelligent extraction of medical information
- **Smart Summarization**: Automated generation of doctor-friendly summaries
- **Real-time Processing**: Asynchronous document processing with status tracking

### Medical Information Extraction
- **Medications**: Automatic detection of prescribed drugs and dosages
- **Vital Signs**: Extraction of blood pressure, heart rate, temperature, weight, height
- **Diagnosis**: Identification of medical conditions and diagnoses
- **Key Findings**: Important observations and test results
- **Risk Assessment**: Urgency level determination and follow-up recommendations

### Doctor Dashboard
- **Document Management**: Upload, view, and manage patient documents
- **Analytics**: Processing statistics and document type distribution
- **Search & Filter**: Find documents by patient name, type, or date
- **Profile Management**: Doctor profile with specialization and credentials

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for text extraction)
- Redis (optional, for async processing)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR:**
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. **Set up the database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   - Main app: http://127.0.0.1:8000/
   - Medical OCR: http://127.0.0.1:8000/medical/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📱 Usage

### For Doctors

1. **Login** to the system using your credentials
2. **Navigate** to Medical OCR section from the main menu
3. **Upload Documents**:
   - Click "Upload Document"
   - Enter patient information
   - Select document type (prescription, lab report, etc.)
   - Upload the file
4. **View Results**:
   - AI summary with key findings
   - Extracted medications and dosages
   - Vital signs and measurements
   - Diagnosis and recommendations
5. **Manage Documents**:
   - View all processed documents
   - Search and filter by patient or type
   - Download summaries
   - Track processing status

### Document Types Supported
- **Prescriptions**: Medication lists and dosages
- **Lab Reports**: Blood tests, urine analysis, etc.
- **Radiology Reports**: X-rays, CT scans, MRI reports
- **Discharge Summaries**: Hospital discharge notes
- **Consultation Notes**: Doctor visit summaries

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini API (Optional - for enhanced AI summaries)
GEMINI_API_KEY=your-gemini-api-key

# Celery/Redis (Optional - for async processing)
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Tesseract Configuration
The system automatically detects Tesseract installation. For Windows, ensure Tesseract is installed in the default location or update the path in `medical_ocr/services.py`.

## 🧠 AI Features

### Text Analysis
- **Medical Entity Recognition**: Identifies medications, conditions, and procedures
- **Pattern Matching**: Extracts vital signs using regex patterns
- **Context Understanding**: Analyzes medical terminology and abbreviations

### Summarization
- **Google Gemini Integration**: Uses Gemini Pro for intelligent summaries (optional)
- **Rule-based Fallback**: Works without API keys using pattern matching
- **Confidence Scoring**: Provides reliability metrics for extracted information

### Risk Assessment
- **Urgency Classification**: Low, Medium, High, Critical
- **Follow-up Detection**: Identifies cases requiring immediate attention
- **Keyword Analysis**: Detects emergency indicators and abnormal values

## 📊 API Endpoints

### Document Management
- `GET /medical/` - Dashboard
- `POST /medical/upload/` - Upload document
- `GET /medical/documents/` - List documents
- `GET /medical/document/{id}/` - Document details

### API Integration
- `GET /medical/api/document/{id}/status/` - Processing status
- `GET /medical/api/document/{id}/summary/` - JSON summary data

## 🔒 Security & Privacy

### Data Protection
- **User Authentication**: Django's built-in user system
- **File Validation**: Secure file upload with type checking
- **Access Control**: Doctors can only access their own documents
- **Data Encryption**: Sensitive data stored securely

### HIPAA Compliance
- **Audit Logging**: Track all document access and modifications
- **Data Retention**: Configurable document retention policies
- **Secure Storage**: Encrypted file storage options

## 🛠️ Development

### Project Structure
```
medical_ocr/
├── models.py          # Database models
├── views.py           # View functions
├── services.py        # OCR and AI processing
├── forms.py           # Django forms
├── tasks.py           # Async processing
├── admin.py           # Admin interface
└── urls.py            # URL routing

templates/medical_ocr/
├── dashboard.html     # Main dashboard
├── upload_document.html
├── document_detail.html
├── document_list.html
├── doctor_profile.html
└── analytics.html
```

### Adding New Document Types
1. Update `DOCUMENT_TYPES` in `models.py`
2. Add extraction patterns in `services.py`
3. Update forms and templates as needed

### Customizing AI Analysis
- Modify `MedicalTextAnalyzer` class in `services.py`
- Add new regex patterns for specific medical terms
- Update summarization prompts for different document types

## 🚨 Troubleshooting

### Common Issues

1. **Tesseract not found**:
   - Ensure Tesseract is installed and in PATH
   - Update path in `services.py` if needed

2. **OCR accuracy issues**:
   - Use high-resolution images
   - Ensure good contrast and lighting
   - Try different image preprocessing settings

3. **Processing failures**:
   - Check file format compatibility
   - Verify file size limits
   - Review error logs in Django admin

4. **Slow processing**:
   - Install Redis for async processing
   - Use Celery workers for background tasks
   - Optimize image preprocessing settings

### Performance Optimization
- **Image Preprocessing**: Adjust parameters in `OCRProcessor.preprocess_image()`
- **Async Processing**: Use Celery for background document processing
- **Caching**: Implement Redis caching for frequent queries
- **Database Indexing**: Add indexes for common search fields

## 📈 Future Enhancements

### Planned Features
- **Mobile App**: Native mobile application for document capture
- **Voice Integration**: Voice-to-text for dictation
- **Multi-language Support**: OCR in multiple languages
- **Integration APIs**: Connect with hospital systems
- **Advanced Analytics**: Machine learning insights
- **Telemedicine**: Video consultation integration

### AI Improvements
- **Custom Models**: Train domain-specific OCR models
- **Medical NLP**: Advanced medical text understanding
- **Predictive Analytics**: Risk prediction algorithms
- **Automated Coding**: ICD-10 code suggestions

## 📞 Support

For technical support or feature requests:
- Check the troubleshooting section above
- Review Django and OCR documentation
- Create an issue in the project repository

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Note**: This system is designed for medical professionals and should be used in compliance with local healthcare regulations and privacy laws.
