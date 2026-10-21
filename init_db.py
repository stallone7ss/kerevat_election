import sqlite3

def setup_database():
    # Connects to the database file (creates it if it doesn't exist)
    conn = sqlite3.connect('election.db')
    cursor = conn.cursor()

    # 1. Reset tables (Optional: clears old data if you are restarting)
    cursor.execute("DROP TABLE IF EXISTS students")
    
    # 2. Create the students table
    cursor.execute('''
        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            has_voted BOOLEAN DEFAULT FALSE
        )
    ''')

    # 3. Add your official Kerevat student IDs here
    allowed_students = [
        ("KNS-2026-0001",),
        ("KNS-2026-0002",),
        ("KNS-2026-0003",),
        # Add as many IDs as you need following this exact pattern
    ]

    # Insert the IDs into the database
    cursor.executemany("INSERT INTO students (student_id) VALUES (?)", allowed_students)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with student IDs!")

if __name__ == "__main__":
    setup_database()
