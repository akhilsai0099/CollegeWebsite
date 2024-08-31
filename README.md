# Course Application Website

## Overview

This project is a web application designed for student course registration, specifically allowing users to apply for honors and minor courses. The application provides a seamless user experience with a focus on responsive design, real-time validation, and robust backend functionalities.

## Features

- **Course Registration**: Allows students to register for available honors and minor courses.
- **User Authentication**: Secure login and registration system to manage student accounts and access control.
- **Data Management**: Efficient handling of course data, user information, and registration records.
- **Responsive Design**: Optimized for various devices, ensuring a consistent experience across desktops, tablets, and smartphones.
- **Real-Time Validation**: Immediate feedback on form submissions and error handling to guide users through the registration process.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (with Django templates).
- **Backend**: Django (Python).
- **Database**: SQLite
- **Authentication**: Django's built-in authentication system.

## Getting Started

### Prerequisites

- Python installed on your system.
- Virtualenv installed for creating isolated Python environments.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akhilsai0099/CollegeWebsite.git
   ```
2. Navigate to the project directory:
   ```bash
   cd CollegeWebsite
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database:
   - Apply migrations to set up the database schema:
     ```bash
     python manage.py migrate
     ```

6. Create a superuser for accessing the Django admin panel:
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Open your browser and navigate to `http://localhost:8000` to start using the application.

### Usage

- **Register/Login**: Create a new account or log in with existing credentials.
- **Browse Courses**: View available honors and minor courses.
- **Apply for Courses**: Select and apply for courses with real-time validation.
- **Admin Interface**: Access the admin panel at `http://localhost:8000/admin` to manage courses and users.
