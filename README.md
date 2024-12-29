# MCQ Quiz Application

A Flask-based web application for conducting multiple-choice questions (MCQ) quizzes with a focus on Environmental Science (EVS) questions.

## Features

- **Dynamic Question Sets**: Questions are divided into sets of 70 questions each
- **Interactive Quiz Interface**: Clean and user-friendly interface for attempting questions
- **Bookmarking System**: Users can bookmark questions for later review
- **Progress Tracking**: Tracks user progress including:
  - Total questions attempted
  - Correct/incorrect answers
  - Accuracy percentage
  - Time taken per question
  - Set-wise statistics
- **Timer Functionality**: Built-in timer for quiz sessions
- **Review Mode**: Ability to review attempted questions and bookmarked questions

## Project Structure

```
mcqs/
├── app.py              # Main application file with Flask routes and logic
├── EVS Questions.txt   # Source file containing MCQ questions
├── requirements.txt    # Python dependencies
├── static/            # Static files (CSS, JS)
├── templates/         # HTML templates
│   ├── index.html    # Main quiz interface
│   └── updates.html  # Updates page
└── wsgi.py           # WSGI entry point
```

## Technical Implementation

### Backend (app.py)
- Built with Flask framework
- Implements question parsing from text file
- Manages user sessions and progress tracking
- Handles quiz logic and scoring
- Provides RESTful endpoints for quiz functionality

### Question Processing
- Questions are parsed from a text file using regex patterns
- Each question contains:
  - Question text
  - Four options (A-D)
  - Correct answer
  - Question number

### User Progress Tracking
- Tracks individual user progress using session management
- Stores:
  - Answered questions
  - Bookmarked questions
  - Time spent per question
  - Set-wise statistics

### Frontend
- Responsive web interface
- Real-time question navigation
- Progress indicators
- Timer display
- Statistical summaries

## Setup and Running

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

## Dependencies

- Flask
- Python 3.x
- Additional requirements listed in requirements.txt

## Deployment

The application is configured for deployment on Vercel with the following files:
- `vercel.json`: Vercel deployment configuration
- `Procfile`: Process file for web server
- `wsgi.py`: WSGI application entry point
