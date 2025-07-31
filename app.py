from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
            );
        ''')

@app.route("/")
def index():
    with sqlite3.connect(DB_NAME) as conn:
        students = conn.execute("SELECT * FROM students").fetchall()
    return render_template("index.html", students=students)

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form["name"]
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO students (name) VALUES (?)", (name,))
    return redirect("/")

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    date = request.form["date"]
    for key in request.form:
        if key.startswith("status_"):
            student_id = key.split("_")[1]
            status = request.form[key]
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                    (student_id, date, status),
                )
    return redirect("/records")

@app.route("/records")
def records():
    with sqlite3.connect(DB_NAME) as conn:
        result = conn.execute("""
            SELECT s.name, a.date, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC
        """).fetchall()
    return render_template("records.html", records=result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
