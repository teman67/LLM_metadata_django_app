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

---

## How to Use These Diagrams in Interview

1. **System Overview**: Use to explain the overall architecture
2. **Request Flow**: Walk through a user interaction step-by-step
3. **Data Flow**: Explain how data moves through the system
4. **Authentication Flow**: Show how security works
5. **Deployment**: Demonstrate production-ready thinking

**Tip**: Draw these on a whiteboard if doing in-person interview!
