import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a persistent secret key in production
DATABASE = 'election.db'
ADMIN_PIN = "kerevat2026"  # Passcode to access the results dashboard

# ================= DATABASE HELPERS ================= #

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema and seeds default data if not present."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # 1. Students table (Tracks authentication and voting status ONLY)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                has_voted INTEGER DEFAULT 0
            )
        ''')

        # 2. Candidates table (Tracks tallies anonymously)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                votes INTEGER DEFAULT 0
            )
        ''')

        # Seed sample authorized students if table is empty
        cursor.execute('SELECT COUNT(*) FROM students')
        if cursor.fetchone()[0] == 0:
            sample_students = [
                ('KNS-2026-1001', 0), ('KNS-2026-1002', 0),
                ('KNS-2026-1003', 0), ('KNS-2026-1004', 0),
                ('KNS-2026-1005', 0), ('KNS-2026-1006', 0),
                ('KNS-2026-1007', 0), ('KNS-2026-1008', 0),
                ('KNS-2026-1009', 0), ('KNS-2026-1010', 0)
            ]
            cursor.executemany('INSERT INTO students (student_id, has_voted) VALUES (?, ?)', sample_students)

        # Seed candidates if table is empty
        cursor.execute('SELECT COUNT(*) FROM candidates')
        if cursor.fetchone()[0] == 0:
            candidates = [
                # Head Boy
                ('Samuel Pokan', 'Head Boy'),
                ('David Vuvu', 'Head Boy'),
                ('Brian Waro', 'Head Boy'),
                
                # Head Girl
                ('Grace Malabag', 'Head Girl'),
                ('Rebecca Kaupa', 'Head Girl'),
                ('Cynthia Toliman', 'Head Girl'),
                
                # Vice Prefect
                ('Emmanuel Auka', 'Vice Prefect'),
                ('Sarah Kila', 'Vice Prefect'),
                ('Jason Maru', 'Vice Prefect'),
                
                # General Prefects (Top 3 can be voted)
                ('Lucas Nali', 'General Prefect'),
                ('Priscilla Teno', 'General Prefect'),
                ('Kevin Bai', 'General Prefect'),
                ('Diana Kove', 'General Prefect'),
                ('Michael Siki', 'General Prefect'),
                ('Angela Tari', 'General Prefect')
            ]
            cursor.executemany('INSERT INTO candidates (name, position) VALUES (?, ?)', candidates)
        conn.commit()

# ================= AUTH DECORATORS ================= #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash("Please enter your Student ID to access the ballot.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ================= ROUTES ================= #

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip().upper()

        if not student_id:
            flash("Student ID is required.", "error")
            return redirect(url_for('index'))

        db = get_db()
        student = db.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)).fetchone()

        if not student:
            flash("Unrecognized Student ID. Please verify your credentials with the electoral committee.", "error")
            return redirect(url_for('index'))

        if student['has_voted'] == 1:
            flash("Our records show that this Student ID has already cast a ballot.", "warning")
            return redirect(url_for('index'))

        # Set session
        session['student_id'] = student_id
        return redirect(url_for('voting'))

    return render_template('index.html')


@app.route('/voting', methods=['GET', 'POST'])
@login_required
def voting():
    student_id = session['student_id']
    db = get_db()

    # Re-verify voter status against database to prevent back-button exploits
    student = db.execute('SELECT has_voted FROM students WHERE student_id = ?', (student_id,)).fetchone()
    if not student or student['has_voted'] == 1:
        session.clear()
        flash("You have already voted or your session is invalid.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        head_boy = request.form.get('head_boy')
        head_girl = request.form.get('head_girl')
        vice_prefect = request.form.get('vice_prefect')
        general_prefects = request.form.getlist('general_prefects')

        # Server-side validation
        if not head_boy or not head_girl or not vice_prefect:
            flash("You must select one candidate for Head Boy, Head Girl, and Vice Prefect.", "error")
            return redirect(url_for('voting'))

        if len(general_prefects) != 3:
            flash("You must select exactly THREE (3) candidates for General Prefects.", "error")
            return redirect(url_for('voting'))

        selected_candidate_ids = [head_boy, head_girl, vice_prefect] + general_prefects

        # Atomic transaction: mark student as voted & record vote counts anonymously
        try:
            with db:
                # Double-check inside transaction lock
                status = db.execute('SELECT has_voted FROM students WHERE student_id = ?', (student_id,)).fetchone()
                if status['has_voted'] == 1:
                    session.clear()
                    flash("Duplicate vote detected. Submission aborted.", "error")
                    return redirect(url_for('index'))

                # Mark student as voted
                db.execute('UPDATE students SET has_voted = 1 WHERE student_id = ?', (student_id,))

                # Increment anonymous candidate tallies
                for cid in selected_candidate_ids:
                    db.execute('UPDATE candidates SET votes = votes + 1 WHERE id = ?', (cid,))

            session.clear()
            flash("Thank you! Your vote has been securely and anonymously recorded.", "success")
            return redirect(url_for('index'))

        except Exception as e:
            flash("An error occurred while processing your vote. Please try again.", "error")
            return redirect(url_for('voting'))

    # Load candidates categorized by position
    candidates = db.execute('SELECT * FROM candidates ORDER BY id ASC').fetchall()
    categorized = {
        'Head Boy': [],
        'Head Girl': [],
        'Vice Prefect': [],
        'General Prefect': []
    }
    for c in candidates:
        if c['position'] in categorized:
            categorized[c['position']].append(c)

    return render_template('voting.html', student_id=student_id, candidates=categorized)


@app.route('/admin-results', methods=['GET', 'POST'])
def admin_results():
    # Simple passkey gate for results view
    is_authenticated = session.get('admin_logged_in', False)

    if request.method == 'POST':
        pin = request.form.get('pin', '')
        if pin == ADMIN_PIN:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_results'))
        else:
            flash("Invalid administrator PIN.", "error")
            return redirect(url_for('admin_results'))

    db = get_db()
    
    # Voter turnout stats
    total_voters = db.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    votes_cast = db.execute('SELECT COUNT(*) as count FROM students WHERE has_voted = 1').fetchone()['count']
    turnout_pct = round((votes_cast / total_voters * 100), 1) if total_voters > 0 else 0

    # Candidate tallies
    candidates = db.execute('SELECT * FROM candidates ORDER BY votes DESC').fetchall()
    categorized = {
        'Head Boy': [],
        'Head Girl': [],
        'Vice Prefect': [],
        'General Prefect': []
    }
    for c in candidates:
        if c['position'] in categorized:
            categorized[c['position']].append(c)

    return render_template(
        'results.html',
        authenticated=is_authenticated,
        total_voters=total_voters,
        votes_cast=votes_cast,
        turnout_pct=turnout_pct,
        results=categorized
    )


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_results'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


import os

if __name__ == '__main__':
    # Reads Render's port 10000 automatically, falls back to 5000 locally
    port = int(os.environ.get("PORT", 1000))
    app.run(host='0.0.0.0', port=port)
