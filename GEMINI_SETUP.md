# Google Gemini API Setup Guide

This guide will help you set up Google Gemini API for enhanced AI summarization in your Medical OCR system.

## 🚀 Getting Your Gemini API Key

### Step 1: Create a Google AI Studio Account
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Accept the terms of service

### Step 2: Generate API Key
1. Click on "Get API Key" in the left sidebar
2. Click "Create API Key" 
3. Choose "Create API key in new project" or select an existing project
4. Copy the generated API key (starts with `AIza...`)

### Step 3: Configure Your Application
1. Create a `.env` file in your project root (if it doesn't exist)
2. Add your API key:
   ```env
   GEMINI_API_KEY=your-api-key-here
   ```
3. Restart your Django server

## 🔧 Testing the Integration

Run the test script to verify everything is working:

```bash
python test_gemini.py
```

You should see:
- ✅ Gemini model initialized successfully!
- AI Model Used: gemini-pro
- A detailed AI-generated summary

## 📊 Features with Gemini

### Enhanced Summarization
- **Contextual Understanding**: Better comprehension of medical terminology
- **Structured Output**: Organized summaries with clear sections
- **Medical Accuracy**: Improved recognition of medical conditions and treatments

### Example Output
```
Patient Summary:
- 45-year-old male presenting with acute chest pain
- Vital signs show elevated blood pressure (150/95) and tachycardia (110 bpm)
- Assessment: Acute coronary syndrome, rule out MI
- Plan: EKG, cardiac enzymes, aspirin, atorvastatin, cardiac monitoring
- Urgency: High - requires immediate cardiac evaluation
```

## 🛡️ Security & Privacy

### API Key Security
- **Never commit API keys to version control**
- **Use environment variables** for configuration
- **Rotate keys regularly** for security
- **Monitor usage** in Google AI Studio dashboard

### Data Privacy
- **No data retention**: Google doesn't store your API requests
- **HIPAA compliance**: Review Google's data processing terms
- **Local processing**: OCR and analysis happen on your server

## 💰 Pricing & Limits

### Free Tier
- **15 requests per minute**
- **1 million tokens per day**
- **Perfect for development and small-scale usage**

### Paid Tier
- **Higher rate limits**
- **Priority support**
- **Enterprise features**

Check current pricing at [Google AI Studio Pricing](https://aistudio.google.com/pricing)

## 🔧 Troubleshooting

### Common Issues

1. **"Gemini model not initialized"**
   - Check if API key is correctly set in `.env`
   - Verify API key format (starts with `AIza`)
   - Ensure internet connection

2. **"API key invalid"**
   - Regenerate API key in Google AI Studio
   - Check for typos in the key
   - Verify the key is active

3. **Rate limit exceeded**
   - Wait for rate limit to reset
   - Consider upgrading to paid tier
   - Implement request queuing

4. **Import errors**
   - Ensure `google-generativeai` is installed: `pip install google-generativeai`
   - Check Python version compatibility

### Debug Mode
Enable debug logging to see detailed error messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Advanced Configuration

### Custom Generation Settings
You can customize the AI generation parameters in `medical_ocr/services.py`:

```python
generation_config=genai.types.GenerationConfig(
    max_output_tokens=500,    # Maximum response length
    temperature=0.3,          # Creativity level (0-1)
    top_p=0.8,               # Nucleus sampling
    top_k=40                 # Top-k sampling
)
```

### Model Selection
Currently using `gemini-pro`. You can experiment with other models:
- `gemini-pro`: Best for text generation
- `gemini-pro-vision`: For image analysis (future feature)

## 📈 Performance Tips

### Optimization
- **Batch requests** when possible
- **Cache results** for repeated queries
- **Use fallback** for offline scenarios
- **Monitor usage** to avoid rate limits

### Best Practices
- **Validate input** before sending to API
- **Handle errors gracefully** with fallback summarization
- **Log API usage** for monitoring
- **Test with various document types**

## 🔄 Migration from OpenAI

If you were previously using OpenAI, the system automatically falls back to rule-based summarization when Gemini is not configured. No code changes needed!

## 📞 Support

### Google AI Studio
- [Documentation](https://ai.google.dev/docs)
- [Community Forum](https://discuss.ai.google.dev/)
- [GitHub Issues](https://github.com/google/generative-ai-python)

### Medical OCR System
- Check the main README for general troubleshooting
- Review Django logs for application-specific issues
- Test with the provided test script

---

**Note**: Always review Google's terms of service and ensure compliance with your organization's data handling policies.


