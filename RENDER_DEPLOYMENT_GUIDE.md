# Render Deployment Guide for AAHAARA-360

This guide will help you deploy your Django application to Render.com.

## Prerequisites

1. A Render.com account
2. Your project repository on GitHub/GitLab
3. Required API keys (Google Gemini)

## Deployment Steps

### 1. Environment Variables

Set these environment variables in your Render dashboard:

#### Required Variables:
- `SECRET_KEY`: Django secret key (Render can generate this automatically)
- `DEBUG`: Set to `False` for production
- `DJANGO_SETTINGS_MODULE`: Set to `myproject.settings_production`
- `GEMINI_API_KEY`: Your Google Gemini API key

#### Optional Variables:
- `FRONTEND_URL`: If you have a separate frontend application
- `CUSTOM_DOMAIN`: If you have a custom domain
- `EMAIL_HOST_USER`: For email functionality
- `EMAIL_HOST_PASSWORD`: For email functionality

### 2. Database Configuration

The `render.yaml` file includes a PostgreSQL database service. Render will automatically provide the `DATABASE_URL` environment variable.

### 3. Static Files

Static files are configured to be served by WhiteNoise. The build process will collect all static files automatically.

### 4. Deployment Process

1. **Connect Repository**: Connect your GitHub/GitLab repository to Render
2. **Create Web Service**: Use the `render.yaml` configuration or create manually:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn myproject.wsgi:application`
   - Environment: Python 3.11
3. **Set Environment Variables**: Add all required environment variables
4. **Deploy**: Render will automatically deploy your application

### 5. Post-Deployment

After deployment:
1. Create a superuser: `python manage.py createsuperuser`
2. Test all functionality
3. Set up custom domain if needed
4. Configure SSL (automatic on Render)

## File Structure

The following files have been created/modified for deployment:

- `requirements.txt`: Production dependencies
- `myproject/settings_production.py`: Production settings
- `render.yaml`: Render configuration
- `build.sh`: Build script
- `start.sh`: Start script
- `RENDER_DEPLOYMENT_GUIDE.md`: This guide

## Troubleshooting

### Common Issues:

1. **Static Files Not Loading**: Ensure `STATIC_ROOT` is set and `collectstatic` runs during build
2. **Database Connection**: Check that `DATABASE_URL` is properly set
3. **CORS Issues**: Update `CORS_ALLOWED_ORIGINS` with your frontend domain
4. **Media Files**: Consider using cloud storage (AWS S3, Cloudinary) for production

### Logs:

Check Render logs for any errors:
- Build logs: Check if all dependencies install correctly
- Runtime logs: Check for application errors

## Security Considerations

1. Never commit sensitive data to version control
2. Use environment variables for all secrets
3. Enable HTTPS (automatic on Render)
4. Regularly update dependencies
5. Monitor application logs

## Performance Optimization

1. Enable caching (Redis recommended for production)
2. Use CDN for static files
3. Optimize database queries
4. Consider using background tasks for heavy operations

## Support

For issues specific to your application, check:
1. Django logs in Render dashboard
2. Application-specific error handling
3. API endpoint responses
