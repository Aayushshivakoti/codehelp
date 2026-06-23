# CodeHelp - Interactive Learning & Coding Platform

Welcome to **CodeHelp**, a comprehensive, gamified platform designed to help users learn programming, solve coding challenges, and take interactive quizzes. Built with a modern tech stack (Vue 3 + Vite for the frontend and Python/Flask + SQLAlchemy for the backend), CodeHelp offers an engaging experience for students and developers to sharpen their skills.

## 🌟 Key Features

- **Gamified Learning**: Earn XP, build learning streaks, and unlock unique **Badges** as you progress. This keeps users motivated to log in daily and complete challenges.
- **Dynamic Quizzes**: Test your knowledge across different Subjects and Chapters with timed multiple-choice quizzes that provide instant feedback.
- **Code Challenges**: Write, compile, and execute code directly in the browser in multiple languages (Python, JavaScript, C++, Java, PHP). Features include hidden test cases, execution time tracking, and memory limits.
- **Tournaments**: Compete in real-time tournaments against other users and climb the leaderboards.
- **AI-Powered Hints**: Get intelligent, AI-generated hints when you are stuck on complex coding challenges without giving away the exact solution.
- **Rich Analytics & Reports**: View detailed statistics of your progress with interactive charts (Chart.js) and export them as PDFs.

## 🧠 Algorithms Used

- **Elo Rating System**: Similar to chess, the platform uses a dynamic Elo rating algorithm to rank users and challenges. Your rating increases when you solve difficult challenges and decreases when you fail, ensuring you are always matched with appropriately difficult questions.
- **Sandboxed Code Execution**: The backend uses an isolated execution environment algorithm to securely compile and run untrusted user code against hidden test cases, measuring execution time and memory footprint safely.
- **Proficiency Indexing**: The system calculates a proficiency index for each user per chapter, creating a recommendation cache that guides users toward topics they need to improve on.

## 📂 Directory Architecture

```text
CodeHelp/
├── backend/                  # Flask Python Backend
│   ├── instance/             # SQLite Database directory
│   ├── templates/            # Email templates (HTML)
│   ├── tests/                # Pytest unit and integration tests
│   ├── app.py                # Main application entry point
│   ├── models.py             # SQLAlchemy Database models
│   ├── jobs.py               # Background scheduled jobs
│   ├── migrate_db.py         # Database migration scripts
│   ├── seed_ai_content.py    # Script to seed default data
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Vue 3 Frontend
│   ├── public/               # Static assets
│   ├── src/                  # Vue source code
│   │   ├── assets/           # CSS and image assets
│   │   ├── components/       # Reusable Vue components (Charts, Filters)
│   │   ├── router/           # Vue Router configuration
│   │   ├── services/         # API interaction logic
│   │   ├── utils/            # Utility functions (e.g. PDF Export)
│   │   ├── views/            # Main page views (Dashboard, Login, Quizzes)
│   │   ├── App.vue           # Root Vue component
│   │   └── main.js           # Vue application entry point
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Vite bundler configuration
│
└── docker-compose.yml        # Docker composition for easy deployment
```

## 🚀 Getting Started

To get the project up and running on your local machine, follow the instructions below. Make sure you have [Node.js](https://nodejs.org/) and [Python 3.x](https://www.python.org/) installed.

### Manual Local Installation

#### 1. Setting up the Backend
1. Navigate to the backend folder: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize the database and migrations: `python migrate_db.py`
6. Run the server: `python app.py`

#### 2. Setting up the Frontend
1. Open a new terminal and navigate to the frontend folder: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Open your browser to the local URL provided by Vite (usually `http://localhost:5173`) to view the application!

## 👥 Default Seed Users

When the database is initialized, the following default users are automatically created so you can log in immediately:

- **Admin Account**
  - **Username:** `admin`
  - **Password:** `admin123`
- **Student Account**
  - **Username:** `student`
  - **Password:** `password123`

## 🧪 Testing

The backend includes a comprehensive test suite to ensure the API and application logic function correctly. 

To run the tests:
1. Ensure your virtual environment is activated (`cd backend` and `venv\Scripts\activate`).
2. Run the pytest command:
   ```bash
   pytest tests/
   ```
This will execute tests for endpoints, lockout logic, and database interactions.

## 📜 License
This project is open-source and available under the MIT License.
