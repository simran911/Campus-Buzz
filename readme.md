# AlumniBuzz Backend

This repository contains the backend code for the **AlumniBuzz** project, built using Flask. The backend manages the server-side logic, routing, and database interactions required for the application.

## Prerequisites

Before setting up and running the project, ensure you have the following installed:

- Python 3.x
- `pip` (Python package installer)

## Setup Guide

Follow these steps to set up and run the backend locally:

### 1. Clone the Repository

```bash
git clone https://github.com/Shubham071122/AlumniBuzz-server.git
cd AlumniBuzz-server
```
### 2. Create a Virtual Environment
- Create a virtual environment to manage dependencies
```bash
python -m venv alumni-server-virtual
```
### 3. Activate the Virtual Environment
- On Windows:
```bash
alumni-server-virtual\Scripts\activate
```
- On macOS/Linux:
```bash
source alumni-server-virtual/bin/activate
```
- You should see the virtual environment name in your terminal, indicating that it’s active.

### 5. Set Up Environment Variables
- Create a .env file in the root of the project (if it doesn't already exist) to store environment-specific variables like Flask settings, database URIs, secret keys, etc.
```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_uri
```

### 6. Run the Flask Application
```bash
python app.py
```
- This will start the server at ` http://127.0.0.1:5000/ ` by default.

### 7. Deactivate the Virtual Environment
- When you’re done working, deactivate the virtual environment:
```bash
deactivate
```
### Happy Coding! 🚀

### Notes:
- Make sure you have a `.gitignore` file that excludes the virtual environment (`alumni-server-virtual/`) and `.env` file from being pushed to GitHub.
- Update any other necessary project-specific information. 

