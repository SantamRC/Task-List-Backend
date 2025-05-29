from flask import Blueprint, request, jsonify
from models import db, User, Task
from datetime import datetime

bp = Blueprint('routes', __name__)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(name=data['name'], username=data['username'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
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
    for field in ['title', 'description', 'status', 'task_type', 'entity_name', 'contact_person', 'due_date', 'user_id']:
        if field in data:
            setattr(task, field, datetime.strptime(data[field], '%Y-%m-%d') if field == 'due_date' else data[field])
    db.session.commit()
    return jsonify({"message": "Task updated"})


@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
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
