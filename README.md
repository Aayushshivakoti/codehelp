# CodeHelp - Interactive Learning & Coding Platform

Welcome to **CodeHelp**, a comprehensive, gamified platform designed to help users learn programming, solve coding challenges, and take interactive quizzes. Built with a modern tech stack (Vue 3 + Vite for the frontend and Python/Flask + SQLAlchemy for the backend), CodeHelp offers an engaging experience for students and developers to sharpen their skills.

## 🚀 Features

- **Gamified Learning**: Earn XP, build learning streaks, and unlock unique **Badges** as you progress.
- **Dynamic Quizzes**: Test your knowledge across different Subjects and Chapters with timed multiple-choice quizzes.
- **Code Challenges**: Write, compile, and execute code in multiple languages (Python, JavaScript, C++, Java, PHP). Features include hidden test cases, execution time tracking, and memory limits.
- **Elo Rating System**: Competitive ranking system that adjusts your Elo score based on your performance in quizzes and challenges.
- **Tournaments**: Compete in real-time tournaments against other users and climb the leaderboards.
- **AI-Powered Hints**: Get intelligent, AI-generated hints when you are stuck on complex coding challenges.
- **Rich Analytics & Reports**: View detailed statistics of your progress with interactive charts and export them as PDFs.

## 🛠️ Tech Stack

### Frontend
- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Routing:** Vue Router
- **Data Visualization:** Chart.js & vue-chartjs
- **Exports:** jsPDF (for generating reports)
- **Markdown:** Marked (for parsing AI hints and challenge descriptions)

### Backend
- **Framework:** Python (Flask)
- **Database ORM:** SQLAlchemy
- **Database:** SQLite (default `quiz_app.db`) / PostgreSQL
- **Environment:** Dedicated runners for executing untrusted code securely

## 📂 Project Structure

- `/frontend` - Contains the Vue 3 application (views, components, routing, and styling).
- `/backend` - Contains the Flask server, database models (`models.py`), API routes, and code execution logic.
- `docker-compose.yml` - For easily containerizing and deploying the full application stack.

## 🏁 Getting Started

### Setting up the Backend
1. Navigate to the backend folder: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize the database: `python migrate_db.py`
6. Run the server: `python app.py`

### Setting up the Frontend
1. Navigate to the frontend folder: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

Open your browser to the local URL provided by Vite (usually `http://localhost:5173`) to view the application!

## 📜 License
This project is open-source and available under the MIT License.
