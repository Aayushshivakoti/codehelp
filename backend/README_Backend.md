# Quiz App Backend Documentation

This document provides documentation for the backend implementation of the Quiz App.

## Project Structure

```
backend/
├── app.py           # Main application file with Flask server and API endpoints
├── jobs.py          # Background jobs and email service implementation
├── migrate_db.py    # Database migration utilities
├── models.py        # Database models and schema definitions
├── requirements.txt # Project dependencies
└── .env            # Environment variables configuration
```

## Technologies Used

- **Flask**: Web framework for the backend API
- **SQLAlchemy**: ORM for database operations
- **JWT**: JSON Web Tokens for authentication
- **CORS**: Cross-Origin Resource Sharing support
- **Schedule**: For background job scheduling
- **bcrypt**: Password hashing
- **python-dotenv**: Environment variable management

## Core Components

### 1. Database Models (`models.py`)

The application uses SQLAlchemy ORM with the following models:

- **User**: Manages user accounts and authentication
  - Fields: id, username, email, password_hash, role, created_at
  - Relationships: quiz_attempts, created_quizzes

- **Subject**: Represents quiz subject categories
  - Fields: id, name, description, is_active, created_by, created_at
  - Relationships: chapters, creator

- **Chapter**: Organizes quizzes within subjects
  - Fields: id, name, description, subject_id, is_active, created_by, created_at
  - Relationships: quizzes, creator

- **Quiz**: Contains quiz information and questions
  - Fields: Various quiz-related fields
  - Relationships: chapter, creator, attempts

### 2. API Server (`app.py`)

The main application file implements:

- **Authentication**: JWT-based authentication system
- **CORS Configuration**: Configured for development environment
- **Database Initialization**: Automatic database setup with sample data
- **API Endpoints**: RESTful endpoints for all operations
- **Error Handling**: JWT and general error handlers

Key Features:
- Automatic admin user creation
- Sample data generation
- Token-based authentication
- Cross-origin request handling

### 3. Background Jobs (`jobs.py`)

Implements scheduled tasks and email services:

- **EmailService**: Handles email notifications
  - SMTP configuration
  - Email validation
  - HTML/Text email support

- **Scheduled Jobs**:
  - User reminders
  - Admin reports
  - Weekly cleanup
  - Inactive user detection
  - Daily statistics

### 4. Dependencies (`requirements.txt`)

Core dependencies:
```
Flask
Flask-JWT-Extended
Flask-CORS
bcrypt
python-dotenv
schedule
sqlalchemy
flask-sqlalchemy
```

## Environment Configuration

The application uses a `.env` file for configuration. Required variables:

- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `SMTP_SERVER`: Email server address
- `SMTP_PORT`: Email server port
- `EMAIL_USER`: Email service username
- `EMAIL_PASSWORD`: Email service password
- `FROM_EMAIL`: Sender email address

## Getting Started

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env` (if available)
   - Set required environment variables

4. Initialize the database:
   ```bash
   python app.py
   ```

The server will create a default admin user with credentials:
- Username: admin
- Password: admin123

## Security Notes

- JWT tokens expire after 24 hours
- Passwords are hashed using bcrypt
- CORS is configured for development (localhost:5173)
- Environment variables should be properly secured in production

## Database Management

- The application uses SQLite by default
- Database file: `quiz_app.db`
- Migrations are handled through `migrate_db.py`
- Automatic schema creation on first run

## API Documentation

The backend provides RESTful APIs for:
- User authentication and management
- Quiz creation and management
- Quiz attempts and scoring
- Subject and chapter organization
- Administrative functions
## Code Execution & Evaluator

The application includes a code execution service powered by the open‑source **Piston** Docker container. Users can submit source code via the `/api/code/run` endpoint and receive real‑time execution results.

### Endpoint

```
POST /api/code/run
Headers:
  Authorization: Bearer <JWT>
Content-Type: application/json

{
  "code": "<source code>",
  "language": "<language identifier>"
}
```

- `code`: The source code to execute.
- `language`: Language identifier supported by Piston (e.g., `python`, `javascript`, `cpp`).

**Response**

```json
{
  "status": "Accepted",
  "output": "Hello\\n",
  "execution_time": 0.12,
  "memory": 5.6
}
```

- `status`: Execution status (e.g., `Accepted`, `Compilation Error`).
- `output`: Combined stdout, stderr, or compile output.
- `execution_time`: Time in seconds.
- `memory`: Memory usage in MB.

### Setup

The Piston service is defined in `docker‑compose.yml` as `quiz_app_piston`. Start it with:

```bash
docker compose up -d quiz_app_piston
```

Ensure the environment variable `PISTON_URL` points to the container (default `http://localhost:2000`).

### Security

Code execution runs inside an isolated Docker container with limited resources. Do not expose the Piston service publicly without additional network restrictions.


Detailed API documentation should be added in a separate document.