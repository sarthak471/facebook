# Facebook Django DRF Project README

## Introduction

Welcome to the Facebook Django DRF project. This README provides step-by-step instructions to set up and run the project on your local development machine. Please ensure you go through all the instructions and files before executing the steps described here.

## Prerequisites

Before you proceed, make sure you have the following requirements met:
* Python 3.8 installed on your system.
* Familiarity with Python virtual environments.
* Basic understanding of Django and Django REST Framework operation.

## This project can be executed without dockers

## Installation

Follow these steps to set up your development environment:

1. **Create a Python virtual environment:**

   Open your terminal and execute the following command:
   
sh
   python3.8 -m venv env
   


2. **Install the required packages:**

   Ensure you are in the project's root directory where the `requirements.txt` file is located, then run:
   
sh
   pip install -r requirements.txt
   


3. **Activate the Python virtual environment:**

   For macOS/Linux:
   
sh
   source env/bin/activate
   

## Running the Project

Once the setup is complete, you can run the Django server:

1. **Navigate to the `facebook` directory:**

   Change to the directory containing your `manage.py` file:
   
sh
   cd facebook
   

2. **Database migrations:**

   Perform database migrations with the following commands:
   
sh
   python manage.py makemigrations
   python manage.py migrate
   


3. **Start the Django development server:**

   Launch your server using:
   
sh
   python manage.py runserver
   


   The server will typically start on port 8000. You can access the web application by visiting `http://127.0.0.1:8000/` in your web browser.
   You can access the django admin panel by visiting `http://127.0.0.1:8000/admin` in your web browser.
   

## Additional Information

- If you encounter issues with migrations, check your database configuration in the `settings.py` file and ensure the database server is running.
- Remember to create new migrations and apply them whenever you make changes to your models.

Thank you for using our Django DRF Project. If you have any questions or need further assistance, please feel free to reach out
