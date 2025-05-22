# Django LLM Metadata Application
A Django web application that provides an interface for interacting with Large Language Models (LLMs) through API calls while storing conversation metadata for analysis and management.


Live webpage: [LLM_Django_app](https://llm-metadata-django-app-835bc5e9a972.herokuapp.com/)

## Features

- **Multi-Model Support**: Interact with various LLM models including Llama 3.3, Qwen3, and Phi4-reasoning
- **Conversation Management**: Store, view, and manage conversation history with detailed metadata
- **File Upload Support**: Upload and process files (.txt, .doc, .json, .csv) as context for conversations
- **Configurable Parameters**: Adjust model parameters like temperature, top-k, top-p, and max tokens
- **User Authentication**: Secure user authentication with Django Allauth
- **Admin Interface**: Django admin panel for managing conversations and metadata
- **JSON Viewer**: Built-in JSON file viewer and table display functionality
- **Responsive Design**: Clean, user-friendly interface

## Project Structure

```
main/
├── LLM_Metadata/           # Main application directory
│   ├── migrations/         # Database migrations
│   ├── templatetags/       # Custom template filters
│   ├── admin.py           # Django admin configuration
│   ├── apps.py            # App configuration
│   ├── forms.py           # Django forms
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   ├── utils.py           # API utility functions
│   └── views.py           # View functions
├── main/                  # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
└── templates/             # HTML templates
```

## Installation

### Prerequisites

- Python 3.8+
- Django 4.2+
- PostgreSQL (for production)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-llm-metadata
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create an `env.py` file or set environment variables:
   ```python
   import os
   
   os.environ["SECRET_KEY"] = "your-secret-key"
   os.environ["DEBUG"] = "True"  # Set to False in production
   os.environ["DATABASE_URL"] = "your-database-url"
   os.environ["API_URL"] = "your-llm-api-endpoint"
   os.environ["API_KEY"] = "your-api-key"
   os.environ["EMAIL_HOST_USER"] = "your-email@gmail.com"
   os.environ["EMAIL_HOST_PASSWORD"] = "your-email-password"
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the application**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Supported Models

The application currently supports these LLM models:
- `llama3.3:70b-instruct-q8_0` - Llama 3.3 70B Instruct
- `qwen3:32b-q8_0` - Qwen3 32B
- `phi4-reasoning:14b-plus-fp16` - Phi4-reasoning 14B

Additional models can be added by modifying the `choices` in `forms.py`.

### Model Parameters

- **Temperature** (0-1): Controls randomness in responses
- **Top K** (0-100): Limits vocabulary selection to top K tokens
- **Top P** (0-1): Nucleus sampling parameter
- **Max Tokens** (1-3000): Maximum response length

### File Upload

Supported file types:
- `.txt` - Text files
- `.doc` - Document files
- `.json` - JSON data files
- `.csv` - CSV data files

Maximum file size: 30MB

## Usage

### Basic Conversation

1. Navigate to `/ask/` to start a new conversation
2. Select your preferred model and adjust parameters
3. Type your question and submit
4. View the AI response and continue the conversation

### File Upload

1. Use the file upload field in the question form
2. Upload supported file types for additional context
3. The file content will be included in the conversation

### Conversation Management

1. Visit `/conversation/` to view conversation history
2. Conversations are grouped by date
3. Delete individual conversations using the delete button

### JSON Viewer

1. Navigate to `/json-viewer/`
2. Upload a JSON file to view formatted content
3. If the JSON contains tabular data, it will display as a table

## Database Models

### Conversation Model

Stores all conversation data with the following fields:

- `role`: 'user' or 'assistant'
- `content`: Message content
- `model_name`: LLM model used
- `token_usage`: Number of tokens in response
- `elapsed_time`: API response time
- `timestamp`: Message timestamp
- `username`: User who created the message
- `conversation_id`: UUID linking related messages
- `temperature`, `top_k`, `top_p`: Model parameters
- `file_upload`: Uploaded file reference

## API Integration

The application uses a custom API utility function (`utils.py`) to communicate with LLM services. The API expects:

```python
payload = {
    "model": model_name,
    "messages": conversation_history,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "top_k": top_k,
    "top_p": top_p
}
```

## Authentication

The application uses Django Allauth for authentication with support for:
- Email/password authentication
- Google OAuth (configurable)
- GitHub OAuth (configurable)

## Admin Interface

Access the Django admin at `/admin/` to:
- View all conversations
- Filter by role, model, and timestamp
- Search conversation content
- Manage user data

## Deployment

### Environment Setup

For production deployment:

1. Set `DEBUG=False`
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend
5. Set secure secret key

### Heroku Deployment

The application is configured for Heroku deployment with:
- `dj-database-url` for database configuration
- Static file handling
- CSRF trusted origins for Heroku domains

### Required Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
- `API_URL`: LLM API endpoint
- `API_KEY`: API authentication key
- `EMAIL_HOST_USER`: SMTP email username
- `EMAIL_HOST_PASSWORD`: SMTP email password

## Development

### Adding New Models

1. Add model choice to `forms.py` in the `QuestionForm.model` field
2. Ensure the API supports the new model
3. Test the integration

### Extending File Support

1. Update `clean_file_upload()` in `forms.py`
2. Add new file types to `valid_extensions`
3. Implement file processing logic if needed

### Custom Template Tags

The application includes custom template tags:
- `conversation_filters.py`: Get assistant responses
- `custom_filters.py`: Add CSS classes to form fields

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify `API_URL` and `API_KEY` are correct
   - Check network connectivity
   - Review API endpoint documentation

2. **File Upload Issues**
   - Ensure file size is under 30MB
   - Check file extension is supported
   - Verify `MEDIA_ROOT` is configured

3. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Check database connection string
   - Ensure database server is running

### Logging

Enable Django logging in `settings.py` for debugging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django documentation
3. Open an issue on the repository
4. Contact the development team (amirhossein.bayani@gmail.com)

## Changelog

### Version 1.0.0
- Initial release
- Multi-model LLM support
- File upload functionality
- Conversation management
- User authentication
- JSON viewer
- Admin interface
