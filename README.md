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
- **🆕 Rate Limiting**: Protect API endpoints from abuse with configurable rate limits
- **🆕 Caching**: Improve performance with intelligent caching of frequently accessed data
- **🆕 REST API**: Clean RESTful API endpoints for programmatic access

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
# Application Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  (HTML/CSS/JavaScript + Bootstrap)                               │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP/HTTPS
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                      Heroku Platform                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Gunicorn WSGI Server                       │ │
│  │                    (Multiple Workers)                        │ │
│  └────────────────┬────────────────────────────────────────────┘ │
│                   │                                               │
│  ┌────────────────▼────────────────────────────────────────────┐ │
│  │                   Django Application                         │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │              URL Router (urls.py)                     │   │ │
│  │  │  / → home                                            │   │ │
│  │  │  /ask/ → ask_question_view                           │   │ │
│  │  │  /conversation/ → conversation_view                   │   │ │
│  │  │  /admin/ → Django Admin                              │   │ │
│  │  │  /accounts/ → Django Allauth                         │   │ │
│  │  └────────────┬─────────────────────────────────────────┘   │ │
│  │               │                                               │ │
│  │  ┌────────────▼─────────────────────────────────────────┐   │ │
│  │  │                  Views (views.py)                     │   │ │
│  │  │  - Business Logic                                     │   │ │
│  │  │  - Request Handling                                   │   │ │
│  │  │  - Response Generation                                │   │ │
│  │  └────┬────────────────────────────────┬─────────────────┘   │ │
│  │       │                                │                     │ │
│  │  ┌────▼──────────┐              ┌─────▼──────────┐          │ │
│  │  │ Forms         │              │ Models          │          │ │
│  │  │ (forms.py)    │              │ (models.py)     │          │ │
│  │  │ - Validation  │              │ - ORM           │          │ │
│  │  │ - Cleaning    │              │ - DB Schema     │          │ │
│  │  └───────────────┘              └────┬────────────┘          │ │
│  │                                      │                        │ │
│  │  ┌───────────────────────────────────▼──────────────────┐   │ │
│  │  │              Templates (templates/)                    │   │ │
│  │  │  - HTML rendering with Django template engine         │   │ │
│  │  └────────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────┬─────────────────────────────────┬──────────────────────────┘
        │                                 │
        │ SQL Queries                     │ HTTP API Calls
        │                                 │
┌───────▼────────────────┐     ┌──────────▼────────────────┐
│  PostgreSQL Database   │     │   External LLM API         │
│  (Supabase/Heroku)     │     │   (Llama, Qwen, etc.)     │
│                        │     │                            │
│  Tables:               │     │   Endpoints:               │
│  - conversations       │     │   - POST /chat             │
│  - auth_user           │     │                            │
│  - django_session      │     │   Authentication:          │
│                        │     │   - Bearer Token           │
└────────────────────────┘     └───────────────────────────┘
```

## Request Flow Diagram

### User Asks Question Flow:

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Navigate to /ask/
     │
┌────▼────────────────────────────────────────────────────────┐
│                  ask_question_view                           │
│                                                               │
│  GET Request:                                                │
│  ├─ Check session for conversation_id                        │
│  ├─ Render empty form                                        │
│  └─ Display previous messages (if any)                       │
│                                                               │
│  POST Request:                                               │
│  ├─ 2. Validate form (QuestionForm)                          │
│  │    ├─ question text                                       │
│  │    ├─ model selection                                     │
│  │    ├─ parameters (temp, top_k, top_p, max_tokens)        │
│  │    └─ optional file upload                                │
│  │                                                            │
│  ├─ 3. Get/Create conversation_id in session                 │
│  │                                                            │
│  ├─ 4. Fetch conversation history from database              │
│  │    └─ SELECT * FROM conversations                         │
│  │       WHERE conversation_id = ?                           │
│  │       ORDER BY timestamp                                  │
│  │                                                            │
│  ├─ 5. Build API payload                                     │
│  │    └─ messages = [                                        │
│  │         {"role": "user", "content": "prev question"},     │
│  │         {"role": "assistant", "content": "prev answer"},  │
│  │         {"role": "user", "content": "new question"}       │
│  │       ]                                                    │
│  │                                                            │
│  ├─ 6. Call query_api(messages, model, params)               │
│  │    │                                                       │
│  │    ├─ POST request to external LLM API                    │
│  │    ├─ Include Bearer token authentication                 │
│  │    ├─ Wait for response                                   │
│  │    └─ Parse response (content, tokens, time)              │
│  │                                                            │
│  ├─ 7. Save user question to database                        │
│  │    └─ INSERT INTO conversations (role='user', ...)        │
│  │                                                            │
│  ├─ 8. Save AI response to database                          │
│  │    └─ INSERT INTO conversations (role='assistant', ...)   │
│  │                                                            │
│  └─ 9. Render template with updated conversation             │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Conversation Model                         │    │
│  │                                                          │    │
│  │  Fields:                                                │    │
│  │  ├─ id (PK)                                             │    │
│  │  ├─ conversation_id (UUID, indexed)                     │    │
│  │  ├─ role ('user' | 'assistant')                         │    │
│  │  ├─ content (TEXT)                                      │    │
│  │  ├─ username (VARCHAR, indexed)                         │    │
│  │  ├─ model_name (VARCHAR)                                │    │
│  │  ├─ token_usage (INT)                                   │    │
│  │  ├─ elapsed_time (FLOAT)                                │    │
│  │  ├─ timestamp (DATETIME, indexed)                       │    │
│  │  ├─ temperature (FLOAT)                                 │    │
│  │  ├─ top_k (INT)                                         │    │
│  │  ├─ top_p (FLOAT)                                       │    │
│  │  └─ file_upload (FILE)                                  │    │
│  │                                                          │    │
│  │  Indexes:                                               │    │
│  │  ├─ conversation_id (for fast conversation lookup)      │    │
│  │  ├─ username (for user filtering)                       │    │
│  │  └─ timestamp (for ordering)                            │    │
│  │                                                          │    │
│  │  Relationships:                                         │    │
│  │  └─ Self-referential via conversation_id                │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Authentication System                      │
│                    (Django Allauth)                           │
│                                                               │
│  Login Options:                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │Email/Pass   │  │Google OAuth  │  │GitHub OAuth  │        │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                │                 │                 │
│         └────────────────┼─────────────────┘                 │
│                          │                                   │
│                ┌─────────▼──────────┐                        │
│                │  Django Session    │                        │
│                │  ├─ session_key    │                        │
│                │  ├─ user_id        │                        │
│                │  └─ expire_date    │                        │
│                └────────────────────┘                        │
│                          │                                   │
│                ┌─────────▼──────────┐                        │
│                │  Session Cookies   │                        │
│                │  (Encrypted)       │                        │
│                └────────────────────┘                        │
│                          │                                   │
│                ┌─────────▼──────────┐                        │
│                │ @login_required    │                        │
│                │ Decorator Check    │                        │
│                └────────────────────┘                        │
│                          │                                   │
│              ┌───────────┴──────────┐                        │
│              │                      │                        │
│         ┌────▼─────┐         ┌─────▼────┐                   │
│         │Authorized│         │Redirect  │                   │
│         │Access    │         │to Login  │                   │
│         └──────────┘         └──────────┘                   │
└──────────────────────────────────────────────────────────────┘
```

## File Upload Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    File Upload Process                       │
│                                                              │
│  1. User selects file                                       │
│     ├─ Supported: .txt, .doc, .json, .csv                   │
│     └─ Max size: 30MB                                       │
│                                                              │
│  2. Form validation (clean_file_upload)                     │
│     ├─ Check file size                                      │
│     ├─ Check file extension                                 │
│     └─ Raise ValidationError if invalid                     │
│                                                              │
│  3. File processing in view                                 │
│     ├─ file_upload = form.cleaned_data.get('file_upload')   │
│     ├─ file_content = file_upload.read().decode('utf-8')    │
│     └─ Append to API messages array                         │
│                                                              │
│  4. Storage                                                 │
│     ├─ Save to media/file_uploads/                          │
│     ├─ Store file reference in database                     │
│     └─ File path: conversation.file_upload.url              │
│                                                              │
│  5. Send to LLM API                                         │
│     └─ messages.append({                                    │
│          "role": "user",                                    │
│          "content": f"File context: {file_content}"         │
│        })                                                   │
└─────────────────────────────────────────────────────────────┘
```

## Conversation Context Management

```
┌─────────────────────────────────────────────────────────────┐
│              Conversation Context System                     │
│                                                              │
│  Session Storage:                                           │
│  ┌────────────────────────────────┐                         │
│  │ request.session                │                         │
│  │ {                              │                         │
│  │   'current_conversation_id':   │                         │
│  │   '550e8400-e29b-41d4-a716'    │                         │
│  │ }                              │                         │
│  └────────────┬───────────────────┘                         │
│               │                                             │
│  ┌────────────▼───────────────────┐                         │
│  │  Database Query                │                         │
│  │  SELECT * FROM conversations   │                         │
│  │  WHERE conversation_id = ?     │                         │
│  │  ORDER BY timestamp ASC        │                         │
│  └────────────┬───────────────────┘                         │
│               │                                             │
│  ┌────────────▼───────────────────┐                         │
│  │  Message History               │                         │
│  │  [                             │                         │
│  │    {role: 'user', content: Q1} │                         │
│  │    {role: 'assistant', A1}     │                         │
│  │    {role: 'user', content: Q2} │                         │
│  │    {role: 'assistant', A2}     │                         │
│  │  ]                             │                         │
│  └────────────┬───────────────────┘                         │
│               │                                             │
│  ┌────────────▼───────────────────┐                         │
│  │  Build API Payload             │                         │
│  │  messages = history + new_msg   │                         │
│  └────────────┬───────────────────┘                         │
│               │                                             │
│  ┌────────────▼───────────────────┐                         │
│  │  Send to LLM API               │                         │
│  │  (Context-aware response)       │                         │
│  └────────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Admin Interface Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Admin Panel                        │
│                      (/admin/)                               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              ConversationAdmin                          │ │
│  │                                                          │ │
│  │  List Display:                                          │ │
│  │  ├─ ID                                                  │ │
│  │  ├─ Role                                                │ │
│  │  ├─ Content (truncated)                                 │ │
│  │  ├─ Model Name                                          │ │
│  │  ├─ Token Usage                                         │ │
│  │  ├─ Elapsed Time                                        │ │
│  │  ├─ Timestamp                                           │ │
│  │  ├─ Username                                            │ │
│  │  └─ Conversation ID                                     │ │
│  │                                                          │ │
│  │  Filters:                                               │ │
│  │  ├─ Role (User/Assistant)                               │ │
│  │  ├─ Model Name                                          │ │
│  │  └─ Timestamp (Date hierarchy)                          │ │
│  │                                                          │ │
│  │  Search:                                                │ │
│  │  ├─ Content                                             │ │
│  │  └─ Username                                            │ │
│  │                                                          │ │
│  │  Actions:                                               │ │
│  │  ├─ View details                                        │ │
│  │  ├─ Edit conversation                                   │ │
│  │  ├─ Delete conversation                                 │ │
│  │  └─ Bulk delete                                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Production Stack                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Heroku Dyno                            │ │
│  │                                                          │ │
│  │  Procfile:                                              │ │
│  │  web: gunicorn main.wsgi:application                    │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────┐          │ │
│  │  │  Gunicorn (WSGI Server)                  │          │ │
│  │  │  - Multiple worker processes              │          │ │
│  │  │  - Handles concurrent requests            │          │ │
│  │  └──────────────┬───────────────────────────┘          │ │
│  │                 │                                        │ │
│  │  ┌──────────────▼───────────────────────────┐          │ │
│  │  │  Django Application                       │          │ │
│  │  │  - DEBUG = False                          │          │ │
│  │  │  - ALLOWED_HOSTS = ['.herokuapp.com']     │          │ │
│  │  └──────────────┬───────────────────────────┘          │ │
│  │                 │                                        │ │
│  │  ┌──────────────▼───────────────────────────┐          │ │
│  │  │  WhiteNoise (Static Files)                │          │ │
│  │  │  - Serves CSS, JS, images                 │          │ │
│  │  │  - Compression enabled                    │          │ │
│  │  │  - Caching headers                        │          │ │
│  │  └───────────────────────────────────────────┘          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  Environment Variables:                                     │
│  ├─ SECRET_KEY                                              │
│  ├─ DATABASE_URL                                            │
│  ├─ API_URL                                                 │
│  ├─ API_KEY                                                 │
│  └─ EMAIL_HOST_USER/PASSWORD                               │
│                                                              │
│  External Services:                                         │
│  ├─ PostgreSQL (Supabase/Heroku)                            │
│  ├─ LLM API (External provider)                             │
│  └─ OAuth Providers (Google, GitHub)                        │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Error Handling System                      │
│                                                              │
│  Form Validation Errors:                                    │
│  ├─ QuestionForm.clean_*() methods                          │
│  ├─ ValidationError raised                                  │
│  └─ Error displayed in template                             │
│                                                              │
│  API Call Errors:                                           │
│  ┌────────────────────────────────────────┐                │
│  │  query_api() function                   │                │
│  │  ├─ Try-except for JSONDecodeError      │                │
│  │  ├─ Check HTTP status code              │                │
│  │  ├─ Validate response structure         │                │
│  │  └─ Return error dict on failure        │                │
│  └────────────┬───────────────────────────┘                │
│               │                                             │
│  ┌────────────▼───────────────────────────┐                │
│  │  View error handling                    │                │
│  │  ├─ Check 'error' key in response       │                │
│  │  ├─ django_messages.error()             │                │
│  │  └─ Display user-friendly message       │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  Database Errors:                                           │
│  ├─ Django ORM handles internally                           │
│  ├─ Transaction rollback on failure                         │
│  └─ IntegrityError for constraint violations                │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Layers                          │
│                                                              │
│  1. Transport Security                                      │
│     ├─ HTTPS enforced (Heroku)                              │
│     └─ TLS 1.2+ encryption                                  │
│                                                              │
│  2. Input Validation                                        │
│     ├─ Form validation (forms.py)                           │
│     ├─ File type checking                                   │
│     ├─ File size limits                                     │
│     └─ Parameter range validation                           │
│                                                              │
│  3. Authentication                                          │
│     ├─ Django session authentication                        │
│     ├─ OAuth 2.0 (Google, GitHub)                           │
│     └─ Password hashing (PBKDF2)                            │
│                                                              │
│  4. Authorization                                           │
│     ├─ @login_required decorators                           │
│     ├─ User-specific data filtering                         │
│     └─ Admin access control                                 │
│                                                              │
│  5. CSRF Protection                                         │
│     ├─ Django CSRF middleware                               │
│     ├─ CSRF tokens in forms                                 │
│     └─ Trusted origins configured                           │
│                                                              │
│  6. SQL Injection Prevention                                │
│     ├─ Django ORM parameterized queries                     │
│     └─ No raw SQL queries                                   │
│                                                              │
│  7. XSS Prevention                                          │
│     ├─ Django template auto-escaping                        │
│     └─ mark_safe() used carefully                           │
│                                                              │
│  8. Secrets Management                                      │
│     ├─ Environment variables                                │
│     ├─ No secrets in code                                   │
│     └─ .gitignore for sensitive files                       │
└─────────────────────────────────────────────────────────────┘
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

### Version 1.1.0 (Latest)
- ✨ **NEW**: Rate limiting for API endpoints to prevent abuse
- ✨ **NEW**: Caching system for improved performance
- ✨ **NEW**: RESTful API endpoints for programmatic access
- ✨ **NEW**: Comprehensive test suite for API functionality
- 📚 **NEW**: Detailed documentation in `RATE_LIMITING_AND_CACHING.md`

### Version 1.0.0
- Initial release
- Multi-model LLM support
- File upload functionality
- Conversation management
- User authentication
- JSON viewer
- Admin interface

## API Endpoints

The application now includes RESTful API endpoints with rate limiting and caching:

### Health Check
```bash
GET /api/health/
# Rate limit: 200 requests/hour
# Cached for 1 minute
```

### Conversation Statistics
```bash
GET /api/conversations/stats/
# Rate limit: 50 requests/hour per user
# Requires authentication
# Cached for 5 minutes per user
```

### Delete Conversation
```bash
DELETE /api/conversations/<uuid>/
# Rate limit: 50 requests/hour per user
# Requires authentication
```

For complete API documentation, see [RATE_LIMITING_AND_CACHING.md](RATE_LIMITING_AND_CACHING.md).
