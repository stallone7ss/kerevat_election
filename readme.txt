# 🗳️ Kerevat National School of Excellence - Student Voting System

A lightweight, secure, and privacy-focused local web application designed to manage the student council elections at Kerevat National School of Excellence. This system handles voting for four major roles: Head Boy, Head Girl, Vice Prefect, and General Prefects.

---

## 📂 Project Structure
Ensure your project directory looks exactly like this on your school laptop:
```text
Kerevat_Elections/
│
├── app.py               # Main Flask application web server
├── init_db.py           # Database setup and student ID loader
├── election.db          # The SQLite database file (auto-generated)
└── templates/           # HTML user interface designs
    ├── index.html       # Voter Login Screen
    ├── voting.html      # Digital Voting Ballot Paper
    └── results.html     # Admin Real-Time Results Dashboard
```

---

## 🛠️ Requirements & Setup Instructions

Follow these sequential steps to set up and run the system locally on your school laptop:

### Step 1: Install Python
1. Download Python for Windows or Mac from [python.org](https://python.org).
2. **Important:** Check the box that says **"Add python.exe to PATH"** during installation.

### Step 2: Install Dependencies
Open your Command Prompt (cmd) or Terminal, navigate to your project folder, and run:
```bash
cd Desktop/Kerevat_Elections
pip install flask
```

### Step 3: Initialize the Database Schema
Before launching the website, you must build the database tables and authorize student IDs. Ensure your `init_db.py` uses the correct `has_voted` column naming scheme.
Run the initialization script:
```bash
python init_db.py
```
*Note: Running this will create a clean `election.db` file. If you delete `election.db` at any point, rerun this step to start fresh.*

### Step 4: Run the Web Server
Launch the active local server using:
```bash
python app.py
```

The terminal will display a local web address. Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔒 Security & Operational Rules

* **Voter Privacy:** Student IDs are logged separately to confirm they have cast a ballot. Individual votes are added anonymously to raw numerical tallies to keep candidate choices strictly confidential.
* **No Database Modifying While Active:** Never edit or save changes to `election.db` via visual software like *DB Browser for SQLite* while the server (`app.py`) is live. Stop the server (`Ctrl + C`) before executing manual database revisions to prevent database-locking errors.

---

## 📊 Viewing Election Results
To check live tallies securely during or after voting, navigate to the admin path:
👉 **`http://127.0.0`**
