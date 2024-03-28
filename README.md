# README for Data Processing Web Application

## Overview

This web application leverages Python and Pandas to process and display data with an emphasis on data type inference and conversion. The backend, built with Django, incorporates a script for handling data types in CSV and Excel files. The frontend, preferably developed using React, provides a user interface for uploading data, initiating processing, and displaying results.

## Getting Started
### Prerequisites
Ensure you have the following installed:

* Python 3.x (3.7 or higher)
* Pip (Python package installer)
* Node.js and npm (Node package manager)
* Python 3.x
* Django

## Backend Setup

Navigate to the dataProject directory:
```
cd data-processing/dataProject
```

Create a virtual environment (optional but recommended):
```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install required Python packages:
```
pip install -r requirements.txt
```

Set up the Django database:
```
python manage.py makemigrations
python manage.py migrate
```
Run the Django development server:
```
python manage.py runserver
```
The backend API will be available at http://127.0.0.1:8000/.




## Frontend Setup
Navigate to the frontend directory:
```
cd frontend
```

Install the necessary npm packages:
```
npm install
```

Start the React development server:
```
npm start
```
The frontend will be available at http://localhost:3000/.

## Using the Application
1. Access the web interface at http://localhost:3000/.
2. Upload a CSV or Excel file to the web application.
3. Submit the file for processing. The application will display inferred data types.
4. Optionally, modify the data types as per your requirements.
5. View the processed data in a user-friendly format on the web application.

## Additional Information
* The data processing script handles a variety of data types and attempts to infer the most accurate types for each column in your dataset.
* If the script encounters columns with mixed types, it will make an educated guess based on the predominant type.
* For large files, the process may take some time. Please be patient as the application processes your data.

## Troubleshooting
* If you encounter any issues with the frontend, check that the backend server is running and accessible.
* For backend issues, ensure all dependencies are installed and database migrations are applied.
