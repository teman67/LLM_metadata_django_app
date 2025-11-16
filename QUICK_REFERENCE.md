# Quick Reference Cheat Sheet for Interview

## 30-Second Elevator Pitch
"I built a Django web application that interfaces with multiple Large Language Models (Llama, Qwen, Mistral, Phi4), storing detailed conversation metadata for analysis. It includes user authentication with OAuth, file upload support, and is deployed on Heroku with PostgreSQL."

## Core Statistics
- **Tech Stack:** Django 4.2.16, Python 3.8+, PostgreSQL, Heroku
- **Lines of Code:** ~500 lines (excluding templates and migrations)
- **Models:** 1 (Conversation model with 12 fields)
- **Views:** 6 main views
- **Templates:** 5 custom templates
- **Supported LLMs:** 4 models (Mistral, Llama 3.3, Qwen3, Phi4)
- **Authentication:** Django Allauth (Email, Google OAuth, GitHub OAuth)

## Key URLs & Views

| URL | View | Purpose |
|-----|------|---------|
| `/` | `home` | Landing page |
| `/ask/` | `ask_question_view` | Main LLM interaction |
| `/conversation/` | `conversation_view` | View conversation history |
| `/json-viewer/` | `json_viewer` | Visualize JSON files |
| `/delete_conversation/<id>/` | `delete_conversation` | Delete conversation thread |
| `/health/` | `health_check` | Database keepalive endpoint |
| `/admin/` | Django admin | Admin interface |
| `/accounts/` | Django Allauth | Authentication |

## Database Model (Conversation)

```python
Conversation:
    - role: 'user' or 'assistant'
    - content: Message text
    - model_name: Which LLM used
    - token_usage: Number of tokens
    - elapsed_time: API response time
    - timestamp: When created
    - username: User who created it
    - conversation_id: UUID linking messages
    - temperature, top_k, top_p: Model parameters
    - file_upload: Optional uploaded file
```

## Key Features (Remember: MCFJA)
1. **M**ulti-model LLM support (4 models)
2. **C**onversation management (history, grouping, deletion)
3. **F**ile upload support (.txt, .doc, .json, .csv, 30MB max)
4. **J**SON viewer (with table conversion)
5. **A**uthentication (OAuth + email/password)
6. **A**dmin interface (filter, search, manage)

## Technology Choices - Why?

| Tech | Why Chosen |
|------|-----------|
| **Django** | Rapid development, built-in admin/auth/ORM, security |
| **PostgreSQL** | Reliability, JSON support, Heroku integration |
| **Django Allauth** | Complete OAuth solution, customizable |
| **Heroku** | Easy deployment, managed services |
| **Gunicorn** | Production-ready WSGI server |
| **WhiteNoise** | Efficient static file serving |

## Critical Code Files

1. **models.py** (34 lines) - Database structure
2. **views.py** (250 lines) - Business logic
3. **forms.py** (104 lines) - Input validation
4. **utils.py** (34 lines) - API integration
5. **settings.py** - Configuration
6. **urls.py** - Routing

## API Integration Flow

```
User Input → QuestionForm Validation → ask_question_view
    ↓
Build messages array from conversation history
    ↓
query_api(messages, model, params)
    ↓
External LLM API (POST request)
    ↓
Parse response (content, tokens, elapsed_time)
    ↓
Save user question + AI response to database
    ↓
Render template with updated conversation
```

## Conversation Context Management

```
Session Storage:
    - 'current_conversation_id' = UUID

Database:
    - All messages with same conversation_id
    - Ordered by timestamp
    - Filtered by username

API Call:
    - Fetch all messages with conversation_id
    - Build messages array: [{"role": "user", "content": "..."}, ...]
    - Send to API for context-aware response
```

## Security Measures (Remember: ECSIXPP)
1. **E**nvironment variables (secrets not in code)
2. **C**SRF protection (Django middleware)
3. **S**QL injection protection (Django ORM)
4. **I**nput validation (forms.py)
5. **X**SS protection (template auto-escaping)
6. **P**assword hashing (PBKDF2)
7. **P**roduction settings (DEBUG=False, HTTPS)

## Common Interview Questions - Quick Answers

**Q: How does conversation context work?**
A: Session stores conversation_id (UUID). Each API call fetches all messages with that ID from database and sends as context to LLM.

**Q: How do you handle API errors?**
A: Try-except for JSON decode, check HTTP status code, return error dict to view, display user-friendly message via Django messages.

**Q: Why UUIDs for conversation IDs?**
A: Security (non-sequential), uniqueness, distribution-ready, future-proof for sharing.

**Q: How would you scale to 10k users?**
A: Database read replicas, Redis caching, Celery for async tasks, CDN for static files, horizontal scaling with multiple Heroku dynos, rate limiting.

**Q: What would you improve?**
A: Add automated tests, implement caching, add async processing with Celery, add analytics dashboard, implement conversation export, add streaming responses.

## Deployment Checklist
- ✅ Environment variables set
- ✅ DEBUG = False
- ✅ PostgreSQL configured
- ✅ Static files collected
- ✅ Migrations applied
- ✅ Gunicorn configured
- ✅ Health check endpoint working
- ✅ CSRF trusted origins set

## Project Strengths to Highlight
1. **Full-stack:** Backend + Frontend + Database + Deployment
2. **Production-ready:** Live on Heroku with PostgreSQL
3. **Security-conscious:** Environment variables, CSRF, validation
4. **Clean architecture:** MVT pattern, separation of concerns
5. **User-focused:** Auth, file uploads, conversation management
6. **Maintainable:** Well-organized code, clear structure

## Weaknesses to Acknowledge
1. No automated tests (would add pytest)
2. No caching layer (would add Redis)
3. Synchronous API calls (could use Celery)
4. Limited error monitoring (would add Sentry)
5. No rate limiting (could add django-ratelimit)

## Demo Flow for Live Walkthrough
1. **Show Homepage** → Clean landing page
2. **Login with OAuth** → Google/GitHub authentication
3. **Ask Question** → Select model, adjust parameters
4. **Upload File** → Demonstrate context addition
5. **View Conversation** → Show history grouped by date
6. **Admin Panel** → Show data management
7. **JSON Viewer** → Upload sample JSON

## Key Metrics to Remember
- **Response Time:** Tracked per message (elapsed_time field)
- **Token Usage:** Tracked per message (token_usage field)
- **Models:** 4 different LLMs available
- **Parameters:** Temperature, Top-K, Top-P, Max Tokens
- **File Size Limit:** 30MB
- **Token Limit:** 1-3000 tokens

## Environment Variables Required
```
SECRET_KEY          # Django secret
DATABASE_URL        # PostgreSQL connection
API_URL            # LLM API endpoint
API_KEY            # LLM API authentication
EMAIL_HOST_USER    # SMTP username
EMAIL_HOST_PASSWORD # SMTP password
DEBUG              # True/False
```

## Git Repository Structure
```
main branch         # Production code
migrations/         # Database schema changes
templates/          # HTML files
static/            # CSS, JS, images
media/             # User uploads
```

## If Asked About Specific Technologies

**Django ORM:**
- Used for all database operations
- Prevents SQL injection
- Supports filtering, ordering, aggregation
- Example: `Conversation.objects.filter(username=request.user).order_by('-timestamp')`

**Django Allauth:**
- Handles authentication flow
- OAuth integration for Google, GitHub
- Email verification, password reset
- Customizable templates

**Gunicorn:**
- Production WSGI server
- Handles multiple concurrent requests
- Configured via Procfile on Heroku

**WhiteNoise:**
- Serves static files efficiently
- No need for separate static file server
- Compression and caching support

## Last-Minute Prep (5 minutes before)
1. ✅ Review this cheat sheet
2. ✅ Test live app URL
3. ✅ Prepare code editor with project open
4. ✅ Review models.py, views.py, forms.py
5. ✅ Practice 30-second pitch
6. ✅ Think of 2-3 challenges you solved
7. ✅ Prepare 2-3 questions for interviewer

## Remember
- **Be confident** - You built a working full-stack app!
- **Be honest** - Acknowledge what you'd improve
- **Show enthusiasm** - Talk about what you learned
- **Ask questions** - Engage with the interviewer
- **Focus on problems solved** - Not just the code

---

**You've got this! Good luck! 🚀**
