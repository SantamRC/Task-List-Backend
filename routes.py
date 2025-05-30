from flask import Blueprint, request, jsonify
from models import db, User, Task
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Task Management API"}), 200


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    # Validate input data
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required.'}), 400

    username = data['username'].strip()

    # Check for empty string
    if not username:
        return jsonify({'error': 'Username cannot be empty.'}), 400

    # Check for duplicate usernames (case-insensitive)
    existing_user = User.query.filter(func.lower(User.username) == username.lower()).first()
    if existing_user:
        return jsonify({'error': 'Username already exists.'}), 409
    

    user = User(name=data['name'], username=data['username'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201




@bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.json

    # Check if 'task' is in the request
    if not data or not data.get('title'):
        return jsonify({'error': 'Task name is required.'}), 400

    task_name = data['title'].strip()

    # Check for empty string after stripping
    if not task_name:
        return jsonify({'error': 'Task name cannot be empty.'}), 400

    # Check if task already exists
    if Task.query.filter_by(title=task_name).first():
        return jsonify({'error': 'Task already exists.'}), 409
    

    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=data.get('status', 'Pending'),
        task_type=data.get('task_type'),
        entity_name=data.get('entity_name'),
        contact_person=data.get('contact_person'),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d') if 'due_date' in data else None,
        user_id=data.get('user_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201




@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    # Check if 'task' is present and validate
    if 'title' in data:
        new_name = data['title'].strip()
        if not new_name:
            return jsonify({'error': 'Task name cannot be empty.'}), 400

    # Check for duplicates only if name is being changed
    if new_name != task.task and Task.query.filter_by(task=new_name).first():
        return jsonify({'error': 'Another task with this name already exists.'}), 409
    task.task = new_name

    # Update status if provided
    if 'status' in data:
        task.status = data['status']


    for field in ['title', 'description', 'status', 'task_type', 'entity_name', 'contact_person', 'due_date', 'user_id']:
        if field in data:
            setattr(task, field, datetime.strptime(data[field], '%Y-%m-%d') if field == 'due_date' else data[field])
    db.session.commit()
    return jsonify({"message": "Task updated"})




@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):

    # Invalidate task_id
    if not isinstance(task_id, int) or task_id <= 0:
        return jsonify({"error": "Invalid task ID"}), 400

    # Check if task exists
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": f"Task with ID {task_id} not found"}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})



@bp.route('/tasks', methods=['GET'])
def get_tasks():
    filters = {}
    for key in ['user_id', 'task_type', 'status', 'entity_name', 'contact_person']:
        value = request.args.get(key)
        if value:
            filters[key] = value

    query = Task.query.filter_by(**filters)

    date_filter = request.args.get('due_date')
    if date_filter:
        query = query.filter(Task.due_date == datetime.strptime(date_filter, '%Y-%m-%d'))

    sort_by = request.args.get('sort_by')
    if sort_by and hasattr(Task, sort_by):
        query = query.order_by(getattr(Task, sort_by))

    tasks = query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "task_type": t.task_type,
        "entity_name": t.entity_name,
        "contact_person": t.contact_person,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "user_id": t.user_id
    } for t in tasks])
