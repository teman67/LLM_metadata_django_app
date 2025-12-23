# Interview Guide: Django LLM Metadata Application

## Quick Overview
A full-stack Django web application that provides an interface for interacting with Large Language Models (LLMs) while storing conversation metadata for analysis and management. The app is deployed on Heroku and integrates with external LLM APIs.

**Live Demo:** [https://llm-metadata-django-app-835bc5e9a972.herokuapp.com/](https://llm-metadata-django-app-835bc5e9a972.herokuapp.com/)

---

## Table of Contents
1. [Application Architecture](#application-architecture)
2. [Core Features](#core-features)
3. [Technical Stack](#technical-stack)
4. [Database Design](#database-design)
5. [Key Components](#key-components)
6. [Security & Authentication](#security--authentication)
7. [Deployment & DevOps](#deployment--devops)
8. [Key Interview Talking Points](#key-interview-talking-points)

---

## Application Architecture

### Project Structure
```
LLM_metadata_django_app/
├── main/                      # Django project configuration
│   ├── settings.py           # Main settings (database, security, apps)
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI server configuration
│   └── asgi.py               # ASGI configuration (async support)
│
├── LLM_Metadata/             # Main application
│   ├── models.py             # Database models (Conversation model)
│   ├── views.py              # View logic (8 views total)
│   ├── forms.py              # Form validation (QuestionForm, ConversationForm)
│   ├── urls.py               # App-level URL routing
│   ├── utils.py              # API integration utilities
│   ├── admin.py              # Django admin customization
│   ├── templatetags/         # Custom template filters
│   │   ├── custom_filters.py
│   │   └── conversation_filters.py
│   └── migrations/           # Database migrations
│
├── templates/                # HTML templates
│   ├── LLM_Metadata/        # App-specific templates
│   │   ├── ask_question.html
│   │   ├── conversation.html
│   │   └── json_viewer.html
│   └── allauth/             # Authentication templates
│
├── static/                   # CSS, JavaScript, images
├── staticfiles/              # Collected static files (production)
├── media/                    # User-uploaded files
└── manage.py                 # Django management script
```

### MVC/MVT Pattern
This application follows Django's **MVT (Model-View-Template)** pattern:
- **Model**: `Conversation` model in `models.py` - handles data structure and database operations
- **View**: Functions in `views.py` - handles business logic and request processing
- **Template**: HTML files in `templates/` - handles presentation layer

---

## Core Features

### 1. **Multi-Model LLM Support**
- **Models Available:**
  - Mistral Small 3.1 (24B parameters)
  - Llama 3.3 (70B parameters)
  - Qwen 3 (32B parameters)
  - Phi4-reasoning (14B parameters)
- **Configurable Parameters:**
  - Temperature (0-1): Controls response randomness
  - Top-K (0-100): Limits token selection pool
  - Top-P (0-1): Nucleus sampling parameter
  - Max Tokens (1-3000): Maximum response length

### 2. **Conversation Management**
- **Features:**
  - Stores complete conversation history
  - Groups conversations by date
  - Maintains conversation context across multiple questions
  - Allows deletion of conversation threads
  - Tracks metadata (tokens, response time, parameters used)

### 3. **File Upload & Processing**
- **Supported Formats:** .txt, .doc, .json, .csv
- **Maximum Size:** 30MB
- **Use Case:** Provides additional context to LLM conversations
- **Validation:** File type and size validation in `forms.py`

### 4. **JSON Viewer**
- **Purpose:** Visualize JSON data in readable format
- **Features:**
  - Displays formatted JSON with indentation
  - Auto-converts JSON arrays to HTML tables
  - Useful for analyzing structured data

### 5. **User Authentication**
- **System:** Django Allauth
- **Methods:**
  - Email/password authentication
  - Google OAuth (configured)
  - GitHub OAuth (configured)
- **Protection:** Login required for conversation features

### 6. **Admin Interface**
- **Access:** `/admin/` endpoint
- **Features:**
  - View all conversations across users
  - Filter by role, model, timestamp
  - Search conversation content
  - Monitor token usage and response times
  - User management

### 7. **Health Check Endpoint**
- **Endpoint:** `/health/`
- **Purpose:** Keep Supabase database active, prevent auto-pause
- **Methods:** GET (read operations), POST (write operations)
- **Response:** JSON with database status and metrics

---

## Technical Stack

### Backend
- **Framework:** Django 4.2.16
- **Language:** Python 3.8+
- **Server:** Gunicorn 20.1.0 (production)
- **API Integration:** Requests library for LLM API calls

### Database
- **Development:** SQLite3 (local)
- **Production:** PostgreSQL (via Supabase/Heroku)
- **ORM:** Django ORM
- **Migrations:** Django migrations system

### Frontend
- **Template Engine:** Django Templates
- **CSS Framework:** Bootstrap (via crispy-bootstrap3)
- **Forms:** Django Crispy Forms
- **JavaScript:** Minimal vanilla JS

### Authentication
- **System:** Django Allauth 65.0.2
- **Features:**
  - OAuth 2.0 (Google, GitHub)
  - Email verification
  - Password management
  - Session management

### Deployment
- **Platform:** Heroku
- **Process:** Gunicorn WSGI server
- **Database:** Supabase PostgreSQL
- **Static Files:** WhiteNoise 6.8.2
- **Environment:** Environment variables for secrets

---

## Database Design

### Conversation Model
The core model that stores all conversation data:

```python
class Conversation(models.Model):
    # Message Data
    role = CharField(max_length=20)              # 'user' or 'assistant'
    content = TextField()                         # Message content
    
    # LLM Metadata
    model_name = CharField(max_length=100)        # Which LLM was used
    token_usage = IntegerField()                  # Number of tokens in response
    elapsed_time = FloatField()                   # API response time in seconds
    
    # Conversation Context
    conversation_id = UUIDField()                 # Links related messages
    timestamp = DateTimeField()                   # When message was created
    username = CharField(max_length=100)          # User who created it
    
    # Model Parameters (for reproducibility)
    temperature = FloatField()
    top_k = IntegerField()
    top_p = FloatField()
    
    # File Handling
    file_upload = FileField()                     # Uploaded files
```

**Key Design Decisions:**
- **UUIDs for conversations:** Allows grouping of related messages in a thread
- **Metadata storage:** Enables analytics on token usage, response times, and parameter effectiveness
- **Parameter tracking:** Allows reproducing exact model behavior
- **Separate role field:** Differentiates between user questions and AI responses

---

## Key Components

### 1. Views (`views.py`)

#### `home(request)`
- **Purpose:** Landing page
- **URL:** `/`
- **Template:** `home.html`

#### `ask_question_view(request)`
- **Purpose:** Main LLM interaction interface
- **URL:** `/ask/`
- **Key Features:**
  - Maintains conversation context via session
  - Validates form input
  - Calls external LLM API
  - Saves both user question and AI response
  - Handles file uploads
- **Session Management:** Uses `current_conversation_id` in session

#### `conversation_view(request)`
- **Purpose:** Display conversation history
- **URL:** `/conversation/`
- **Key Features:**
  - Groups conversations by date
  - Pairs user/assistant messages
  - Filters by logged-in user
  - Supports conversation deletion

#### `json_viewer(request)`
- **Purpose:** JSON file visualization
- **URL:** `/json-viewer/`
- **Features:**
  - Uploads and parses JSON files
  - Displays formatted JSON
  - Converts arrays to tables

#### `delete_conversation(request, user_convo_id)`
- **Purpose:** Delete conversation threads
- **URL:** `/delete_conversation/<id>/`
- **Method:** POST only
- **Logic:** Deletes all messages with same `conversation_id`

#### `health_check(request)`
- **Purpose:** Database keepalive endpoint
- **URL:** `/health/`
- **Methods:** GET and POST
- **Features:**
  - Tests database connection
  - Returns metrics (conversation count, latest timestamp)
  - Creates/deletes test records on POST

### 2. Forms (`forms.py`)

#### `QuestionForm`
- **Purpose:** Validate LLM interaction inputs
- **Fields:**
  - `question`: TextArea for user input
  - `model`: ChoiceField for LLM selection
  - `max_tokens`: IntegerField (1-3000)
  - `temperature`: FloatField (0-1)
  - `top_k`: IntegerField (0-100)
  - `top_p`: FloatField (0-1)
  - `file_upload`: FileField (optional)
- **Custom Validation:**
  - File size limit (30MB)
  - File type validation
  - Parameter range validation

#### `ConversationForm`
- **Purpose:** Simple conversation creation (legacy/testing)
- **Fields:** `content` only

### 3. API Integration (`utils.py`)

#### `query_api(messages, model, temperature, max_tokens, top_k, top_p)`
- **Purpose:** Communicate with external LLM API
- **Configuration:**
  - API URL from environment variable
  - Bearer token authentication
- **Payload Structure:**
  ```python
  {
      "model": "llama3.3:70b-instruct-q8_0",
      "messages": [{"role": "user", "content": "..."}],
      "temperature": 0.7,
      "max_tokens": 600,
      "top_k": 40,
      "top_p": 0.9
  }
  ```
- **Error Handling:**
  - JSON decode errors
  - HTTP status code validation
  - Returns error messages to view layer

### 4. Custom Template Tags

#### `conversation_filters.py`
- **Purpose:** Extract assistant responses from conversations
- **Filter:** `get_assistant_response` - retrieves AI response for a given conversation

#### `custom_filters.py`
- **Purpose:** Add CSS classes to form fields
- **Filter:** `add_class` - applies Bootstrap classes to form elements

### 5. Admin Configuration (`admin.py`)

```python
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'content', 'model_name', 
                    'token_usage', 'elapsed_time', 'timestamp', 
                    'username', 'conversation_id')
    list_filter = ('role', 'model_name', 'timestamp')
    search_fields = ('content', 'username__username')
    ordering = ('-timestamp',)
```

**Features:**
- Comprehensive list view with all key fields
- Filter by role, model, and timestamp
- Search through conversation content
- Ordered by most recent first

---

## Security & Authentication

### Environment Variables
Sensitive data stored in environment variables (not in code):
```python
SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
API_URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
```

### Security Measures
1. **Debug Mode:** Set to `False` in production
2. **CSRF Protection:** Django middleware enabled
3. **Trusted Origins:** Configured for Heroku and development domains
4. **Login Required:** `@login_required` decorator on sensitive views
5. **Password Validation:** Django's built-in validators
6. **SQL Injection:** Protected by Django ORM
7. **XSS Protection:** Django template auto-escaping

### Authentication Flow
1. User visits site → redirected to login if not authenticated
2. User can log in via:
   - Email/password
   - Google OAuth
   - GitHub OAuth
3. Django Allauth manages sessions
4. User-specific data filtered by `request.user`

---

## Deployment & DevOps

### Heroku Configuration
- **Procfile:** Defines Gunicorn server command
- **Runtime:** Python 3.8+
- **Buildpacks:** Python buildpack
- **Database:** Heroku PostgreSQL or Supabase
- **Static Files:** Collected via WhiteNoise

### Database Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Environment Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up `env.py` with required variables
5. Run migrations
6. Start development server: `python manage.py runserver`

### Production Considerations
- **Static Files:** Collected to `staticfiles/` directory
- **Media Files:** Uploaded to `media/` directory
- **Database:** PostgreSQL recommended for production
- **HTTPS:** Enforced via Heroku
- **Monitoring:** Health check endpoint for uptime monitoring

---

## Key Interview Talking Points

### 1. **Project Motivation & Purpose**
> "I built this application to solve the problem of managing and analyzing LLM interactions. While many chat interfaces exist, they don't provide detailed metadata about token usage, response times, or parameter configurations. This app fills that gap by storing all conversation metadata, enabling users to analyze which models and parameters work best for their use cases."

### 2. **Technical Challenges Solved**

#### Challenge 1: Maintaining Conversation Context
**Problem:** LLM APIs are stateless, but users expect conversational context.
**Solution:** Implemented session-based conversation IDs and built conversation history from database for each API call.

#### Challenge 2: File Upload Integration
**Problem:** Users want to provide additional context via files.
**Solution:** Implemented file upload with validation, read file content, and append to API messages array.

#### Challenge 3: Database Auto-Pause
**Problem:** Supabase free tier pauses inactive databases.
**Solution:** Created health check endpoint with GET/POST operations to maintain activity.

### 3. **Design Decisions**

#### Why Django?
- **Rapid Development:** Built-in admin, ORM, authentication
- **Security:** Battle-tested framework with built-in protections
- **Scalability:** Easy to scale with proper architecture
- **Community:** Large ecosystem of packages (Allauth, Crispy Forms)

#### Why PostgreSQL?
- **Reliability:** Industry-standard relational database
- **JSON Support:** Can store JSON data if needed
- **Heroku Integration:** Native support and easy setup
- **ACID Compliance:** Data integrity guaranteed

#### Why Allauth?
- **OAuth Support:** Easy integration with Google, GitHub
- **Complete Solution:** Email verification, password reset built-in
- **Customizable:** Can override templates and forms
- **Maintained:** Active development and security updates

### 4. **Performance Optimizations**
- **Database Indexing:** Timestamp and conversation_id indexed for fast queries
- **Query Optimization:** Filter conversations by user to reduce data transfer
- **Static Files:** WhiteNoise serves static files efficiently
- **Session Management:** Uses conversation_id in session to avoid redundant queries

### 5. **Scalability Considerations**
- **Database:** PostgreSQL can handle millions of records
- **Caching:** Could add Redis for session storage
- **API Calls:** Async implementation possible with Django Channels
- **Load Balancing:** Heroku supports multiple dynos
- **CDN:** Could serve static files via CDN

### 6. **Testing Strategy**
- **Unit Tests:** Test form validation, model methods
- **Integration Tests:** Test view logic, API integration
- **Manual Testing:** User flows, edge cases
- **Security Testing:** CSRF, XSS, SQL injection

### 7. **Future Enhancements**
1. **Analytics Dashboard:** Visualize token usage, response times over time
2. **Export Feature:** Export conversations to PDF or CSV
3. **Model Comparison:** Side-by-side comparison of different models
4. **Streaming Responses:** Real-time display of LLM responses
5. **Conversation Sharing:** Share conversations via unique links
6. **Rate Limiting:** Prevent API abuse
7. **Cost Tracking:** Monitor API costs per user
8. **Advanced Search:** Full-text search across all conversations

### 8. **Lessons Learned**
- **Environment Variables:** Critical for security and deployment flexibility
- **Error Handling:** Always validate external API responses
- **User Experience:** Session management is key for conversational interfaces
- **Database Design:** UUID for conversation grouping was the right choice
- **Testing:** Should have implemented automated tests earlier

### 9. **What Would You Do Differently?**
- **Add Tests:** Implement comprehensive test suite from the start
- **API Versioning:** Design API integration with versioning in mind
- **Caching:** Implement caching for frequently accessed data
- **Async Processing:** Use Celery for background tasks
- **Monitoring:** Add application performance monitoring (APM)
- **Documentation:** API documentation for potential future API endpoints

### 10. **How to Explain This Project**

**Elevator Pitch (30 seconds):**
> "I built a Django web application that provides an interface for interacting with various Large Language Models while storing detailed metadata about each conversation. It supports multiple LLM models, file uploads for context, and includes user authentication with OAuth. The app is deployed on Heroku with PostgreSQL, and I designed it to help users analyze which models and parameters work best for their specific use cases."

**Technical Deep Dive (2 minutes):**
> "The application follows Django's MVT architecture with a single Conversation model that stores both user questions and AI responses using a role field. I implemented session-based conversation context management, where each conversation thread is identified by a UUID stored in the session. 
>
> For the LLM integration, I created a utility function that communicates with external APIs via HTTP requests, sending conversation history and configurable parameters like temperature and top-k. The app validates all user inputs through Django forms with custom validation logic.
>
> For authentication, I integrated Django Allauth to support both traditional email/password login and OAuth with Google and GitHub. The admin interface provides full visibility into conversations and metadata for analysis.
>
> The deployment on Heroku uses Gunicorn as the WSGI server, PostgreSQL for the database, and WhiteNoise for static file serving. I also implemented a health check endpoint to prevent database auto-pause on free tier hosting."

---

## Common Interview Questions & Answers

### Q: "Walk me through how a user interacts with an LLM in your app."

**Answer:**
1. User logs in via Django Allauth (email/password or OAuth)
2. Navigates to `/ask/` route, which renders `ask_question.html`
3. Fills out `QuestionForm` with their question, selects a model, and adjusts parameters
4. Optionally uploads a file for additional context
5. Form submission triggers `ask_question_view`:
   - Validates form data
   - Retrieves or creates conversation ID from session
   - Fetches conversation history from database
   - Builds API payload with messages array
   - Calls `query_api()` utility function
   - Saves both user question and AI response to database
   - Renders template with updated conversation
6. User can continue conversation; context is maintained via conversation_id

### Q: "How do you handle API failures?"

**Answer:**
I implemented multiple layers of error handling:
1. **HTTP Status Codes:** Check if response.status_code == 200
2. **JSON Validation:** Try-except block for JSON decode errors
3. **Response Structure:** Verify expected fields exist in response
4. **User Feedback:** Display user-friendly error messages via Django messages framework
5. **Logging:** Could add logging for debugging (not currently implemented)
6. **Fallback:** Return error dict to view layer instead of raising exceptions

### Q: "Why use UUIDs for conversation IDs instead of auto-incrementing integers?"

**Answer:**
- **Security:** Non-sequential, harder to guess other users' conversations
- **Distribution:** UUIDs work well in distributed systems
- **Uniqueness:** Guaranteed unique across database without coordination
- **URL Sharing:** In future, could share conversations via UUID links
- **No Collisions:** Multiple servers can generate IDs without conflicts

### Q: "How does your app handle concurrent users?"

**Answer:**
- **Session Isolation:** Each user has their own session with unique conversation_id
- **Database Transactions:** Django ORM handles concurrent writes safely
- **User Filtering:** Queries always filter by `request.user`
- **Stateless API:** LLM API calls are independent
- **Gunicorn Workers:** Multiple workers can handle concurrent requests
- **Future:** Could add connection pooling and caching for better concurrency

### Q: "What security measures did you implement?"

**Answer:**
1. **Environment Variables:** All secrets in environment, not code
2. **CSRF Protection:** Django middleware prevents cross-site attacks
3. **Authentication:** Login required on sensitive views
4. **Input Validation:** Form validation prevents malicious input
5. **SQL Injection:** Django ORM parameterizes queries
6. **XSS Protection:** Django templates auto-escape HTML
7. **HTTPS:** Enforced on Heroku
8. **Password Hashing:** Django's built-in PBKDF2 algorithm
9. **OAuth:** Secure authentication via trusted providers

### Q: "How would you scale this application to handle 10,000+ users?"

**Answer:**
1. **Database:**
   - Move to managed PostgreSQL with read replicas
   - Add database indexing on frequently queried fields
   - Implement connection pooling
2. **Caching:**
   - Add Redis for session storage
   - Cache frequently accessed conversations
   - Cache LLM model list
3. **API Calls:**
   - Implement queue system (Celery + Redis)
   - Batch API requests where possible
   - Add retry logic with exponential backoff
4. **Static Files:**
   - Move to CDN (CloudFront, Cloudflare)
   - Compress assets
5. **Application:**
   - Horizontal scaling: Multiple Heroku dynos
   - Load balancing: Heroku's built-in load balancer
   - Monitoring: Add APM (New Relic, Datadog)
6. **Rate Limiting:**
   - Implement per-user rate limiting
   - Add API quotas

---

## Quick Reference: Files to Review Before Interview

### Must Review:
1. **README.md** - Project overview and setup
2. **models.py** - Database structure
3. **views.py** - Core business logic
4. **forms.py** - Input validation
5. **utils.py** - API integration
6. **settings.py** - Configuration

### Nice to Review:
1. **urls.py** - Routing structure
2. **admin.py** - Admin customization
3. **templates/** - UI structure

### Don't Need to Review:
1. **migrations/** - Auto-generated
2. **staticfiles/** - Collected static files
3. **allauth templates** - Third-party package

---

## Final Tips for Interview

### Be Prepared to:
1. **Demonstrate:** Show the live app or local instance
2. **Explain Tradeoffs:** Why you chose certain technologies
3. **Discuss Alternatives:** What other approaches you considered
4. **Identify Weaknesses:** Be honest about what could be improved
5. **Show Growth Mindset:** Talk about what you learned
6. **Code Walkthrough:** Be ready to walk through any file

### Key Strengths to Emphasize:
- Full-stack development (backend, frontend, database, deployment)
- API integration and error handling
- User authentication with OAuth
- Database design and ORM usage
- Security best practices
- Production deployment experience
- Clean, maintainable code structure

### Practice Explaining:
- Why Django over Flask or FastAPI?
- How does session-based conversation context work?
- What's your development workflow?
- How do you debug issues in production?

---

## Conclusion

This Django LLM Metadata application demonstrates:
- ✅ Full-stack web development skills
- ✅ Database design and ORM proficiency
- ✅ API integration and error handling
- ✅ User authentication and security
- ✅ Production deployment experience
- ✅ Clean code and project organization

**Remember:** Focus on the problems you solved, the decisions you made, and what you learned. The code is just the implementation of your thought process!

Good luck with your interview! 🚀
