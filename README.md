# Interactive MCQ Quiz Application

An interactive Multiple Choice Questions (MCQ) quiz application built with Flask, featuring immediate feedback and a modern user interface.

## 🌟 Features

- **Immediate Feedback**: Get instant feedback on your answers
- **Visual Indicators**: 
  - ✅ Green checkmark for correct answers
  - ❌ Red X for incorrect answers
  - Automatic display of correct answer when wrong choice is selected
- **User-Friendly Navigation**:
  - Previous/Next buttons
  - Question status tracking
  - Easy-to-use interface
- **Responsive Design**: Works on both desktop and mobile devices
- **Score Tracking**: Keep track of your performance

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository
```bash
git clone https://github.com/Ktripathi2611/practicemcq.git
cd practicemcq
```

2. Install required packages
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask server
```bash
python app.py
```

2. Open your browser and navigate to
```
http://localhost:5000
```

## 📖 Usage

1. **Taking the Quiz**:
   - Read each question carefully
   - Select one answer from the options provided
   - Get immediate feedback on your selection
   - Navigate through questions using Previous/Next buttons

2. **Understanding Feedback**:
   - Green background: Correct answer
   - Red background: Incorrect answer
   - When wrong answer selected: The correct answer is highlighted

## 🛠️ Technical Details

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Flask (Python)
- **Dependencies**: 
  - Flask 3.0.0
  - Werkzeug 3.0.1
  - Gunicorn 21.2.0 (for production)

## 📱 Deployment

### Heroku Deployment

1. Install Heroku CLI and login
```bash
heroku login
```

2. Create a new Heroku app
```bash
heroku create your-app-name
```

3. Deploy the application
```bash
git push heroku main
```

### Other Platforms

The application can be deployed to any platform that supports Python web applications:
- PythonAnywhere
- DigitalOcean
- AWS
- Google Cloud Platform

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework community
- Contributors and testers
- Everyone who provided feedback and suggestions
