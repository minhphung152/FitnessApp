# Health Tracker - Weight & Food Tracking App

[![Django Version](https://img.shields.io/badge/Django-4.2-brightgreen)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

A web application for tracking daily weight, food consumption, and calorie goals.

---

## Features

- **User Authentication**: 
    - Secure registration and login system.
    - Password reset functionality.

- **Weight Tracking**: 
    - Record daily weight entries.
    - View weight history with a progress chart.

- **Food Tracking**: 
    - Log food entries with calorie, protein, fat, and carbs information.
    - Search for food items using the USDA Food Database API.

- **Dashboard**: 
    - Overview of recent weight and food entries.
    - Visualize progress toward calorie and weight goals.

- **Responsive Design**:
    - Fully responsive UI built with Bootstrap for seamless use on desktop and mobile devices.

--- 

## Installation

### Prerequisites
- Python 3.8 or higher
- Django 4.2 or higher

### Steps
1. Clone the repository:
```bash
git clone https://github.com/minhphung152/fitness_app.git
cd fitness_app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

7. Open the app in your browser:
```bash
http://127.0.0.1:8000/
```

## Usage
1. **Register an account**: Create a new account or log in with existing credentials.
2. **Track Weight**: Add daily weight entries and view progress on the dashboard.
3. **Log Food**: Search for food items and log them to track calorie intake.
4. **Monitor Progress**: Use the dashboard to visualize weight trends and calorie goals.