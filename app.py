from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DB Connection
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT version();')
    db_version = cur.fetchone()
    cur.close()
    conn.close()
    return f'Connected to: {db_version[0]} and the DB URL is {os.getenv("DATABASE_URL")}'



# Create Task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    description = data.get("description")
    if not description:
        return jsonify({"error": "Description is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (description) VALUES (%s) RETURNING *;", (description,))
    new_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_task), 201


# Get All Tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(tasks)

# Get Task by ID
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

# Update Task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    description = data.get("description")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET description = %s WHERE id = %s RETURNING *;", (description, task_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return jsonify(updated)
    return jsonify({"error": "Task not found"}), 404

# Delete Task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s RETURNING *;", (task_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return jsonify({"message": "Task deleted"})
    return jsonify({"error": "Task not found"}), 404


if __name__ == "__main__":
    app.run()
