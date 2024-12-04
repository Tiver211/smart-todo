import uuid
from datetime import timedelta

from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from flask_login import current_user, login_required

from app.models import Group, Hashtag, TaskHashtag
from app.services.tasks_control_service.tasks_control_service import *
from app.extensions import logger

tasks_control_bp = Blueprint('tasks_control', __name__)


@tasks_control_bp.before_request
def assign_operation_id():
    # Генерируем уникальный идентификатор операции
    g.operation_id = str(uuid.uuid4())
    # Логируем начало обработки запроса
    logger.info(f"Начало обработки запроса {request.path}", extra={"operation_id": g.operation_id})


@tasks_control_bp.after_request
def after_request(response):
    logger.info("Обработка запроса завершена", extra={"operation_id": g.operation_id})
    return response


@tasks_control_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = current_user.user_id
    logger.info("Получение всех заданий", extra={"operation_id": g.operation_id})

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        task_data = {
            'task_id': task.task_id,
            'title': task.shared_attributes.title,
            'description': task.shared_attributes.description,
            'priority': task.shared_attributes.priority,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }
        result.append(task_data)

    logger.info("Задания получены", extra={"operation_id": g.operation_id})
    return jsonify(result)


@tasks_control_bp.route('/task/delete/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    user_id = current_user.user_id
    

    logger.info(f"Попытка удалить задачу с ID {task_id}", extra={"operation_id": g.operation_id})

    task = Task.query.filter_by(user_id=user_id, task_id=task_id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        logger.info(f"Задача с ID {task_id} успешно удалена", extra={"operation_id": g.operation_id})
        return jsonify({'message': 'Task deleted'})

    logger.error(f"Задача с ID {task_id} не найдена или не принадлежит пользователю",
                 extra={"operation_id": g.operation_id})
    return jsonify({'error': 'Task not found or does not belong to this user'}), 404


@tasks_control_bp.route('/task/update/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    user_id = current_user.user_id
    

    logger.info(f"Попытка обновить задачу с ID {task_id}", extra={"operation_id": g.operation_id})

    task = Task.query.filter_by(user_id=user_id, task_id=task_id).first()
    if not task:
        logger.error(f"Задача с ID {task_id} не найдена или не принадлежит пользователю",
                     extra={"operation_id": g.operation_id})
        return jsonify({'error': 'Task not found or does not belong to this user'}), 404

    data = request.get_json()
    for key, value in data.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.session.commit()

    logger.info(f"Задача с ID {task_id} успешно обновлена", extra={"operation_id": g.operation_id})
    return jsonify({'message': 'Task updated', 'task': task_id})


@tasks_control_bp.route('/task/add', methods=['POST'])
@login_required
def add_task():
    try:
        user_id = current_user.user_id

        logger.info("Добавление нового задания", extra={"operation_id": g.operation_id})

        data = request.get_json()
        shared = SharedAttributes(
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            able_to_split=bool(data['able_to_split']),
            compilable=bool(data['compilable']),
            duration=timedelta(data['duration']),
            force_time_start=data.get('force_time_start'),
            force_end_time=data.get('force_time_end'),
            day_period=data.get('day_period'),
            status=data.get('status'),
        )
        db.session.add(shared)
        db.session.commit()
        print(shared.shared_id)
        task = Task(
            user_id=user_id,
            shared_id=shared.shared_id,
            parent=data.get('parent_id'),
            group_id=data.get('group_id'),
            reapeated_from=data.get('reapeted_from')
        )
        db.session.add(task)
        db.session.commit()

        logger.info(f"Задача с ID {task.task_id} успешно добавлена", extra={"operation_id": g.operation_id})
        return jsonify({'message': 'Task created', 'task_id': task.task_id}), 201
    except Exception as e:
        logger.error(e, extra={"operation_id": g.operation_id})
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_control_bp.route('/group/add', methods=['POST'])
@login_required
def create_group():
    user_id = current_user.user_id
    

    logger.info("Создание группы", extra={"operation_id": g.operation_id})

    data = request.get_json()
    shared = SharedAttributes(
            title=data['title'],
            description=data['description'],
            priority=data['priority'],
            able_to_split=bool(data['able_to_split']),
            compilable=bool(data['compilable']),
            duration=timedelta(data['duration']),
            force_time_start=data.get('force_time_start'),
            force_end_time=data.get('force_time_end'),
            day_period=data.get('day_period'),
            status=data.get('status'),
        )
    db.session.add(shared)
    db.session.commit()

    group = Group(
        user_id=user_id,
        shared_id=shared.shared_id,
        parent=data.get('parent_id'),
        group_id=data.get('group_id')
    )
    db.session.add(group)
    db.session.commit()

    logger.info(f"Группа с ID {group.group_id} успешно создана", extra={"operation_id": g.operation_id})
    return jsonify({'message': 'Group created', 'group_id': group.group_id}), 201


@tasks_control_bp.route('/groups', methods=['GET'])
@login_required
def get_groups():
    user_id = current_user.user_id
    groups = Group.query.filter_by(user_id=user_id).all()
    result = []
    for group in groups:
        group_data = {
            'group_id': group.group_id,
            'title': group.shared_attributes.title,
            'description': group.shared_attributes.description,
            'created_at': group.created_at
        }
        result.append(group_data)
    return jsonify(result)


@tasks_control_bp.route('/group/update/<int:group_id>', methods=['PUT'])
@login_required
def update_group(group_id):
    user_id = current_user.user_id
    group = Group.query.filter_by(user_id=user_id, group_id=group_id).first()

    if not group:
        logger.error(f"Группа с ID {group_id} не найдена или не принадлежит пользователю",
                     extra={"operation_id": g.operation_id})
        return jsonify({'error': 'group not found or does not belong to this user'}), 404

    data = request.get_json()
    for key, value in data.items():
        if hasattr(group, key):
            setattr(group, key, value)
    db.session.commit()

    logger.info(f"Задача с ID {group_id} успешно обновлена", extra={"operation_id": g.operation_id})
    return jsonify({'message': 'group updated', 'group': group_id})


@tasks_control_bp.route('/repeated_task/create', methods=['POST'])
@login_required
def add_repeated_task():
    user_id = current_user.user_id
    

    logger.info("Создание повторяющегося задания", extra={"operation_id": g.operation_id})

    data = request.get_json()

    repeated_task = RepeatingTask(
        user_id=user_id,
        repeat_pattern=data['repeat_pattern'],
        parent=data.get('parent_id'),
        group_id=data.get('group_id'),
        shared_id=data['shared_id']
    )
    db.session.add(repeated_task)
    db.session.commit()

    logger.info(f"Повторяющееся задание с ID {repeated_task.repeat_id} успешно добавлено",
                extra={"operation_id": g.operation_id})
    return jsonify({'message': 'Repeated task created', 'repeat_id': repeated_task.repeat_id}), 201


@tasks_control_bp.route('/repeated_task/update/<int:repeat_id>', methods=['PUT'])
@login_required
def update_repeated_task(repeat_id):
    user_id = current_user.user_id
    

    logger.info(f"Обновление повторяющегося задания с ID {repeat_id}", extra={"operation_id": g.operation_id})

    repeated_task = RepeatingTask.query.filter_by(user_id=user_id, repeat_id=repeat_id).first()
    if not repeated_task:
        logger.error(f"Повторяющееся задание с ID {repeat_id} не найдено", extra={"operation_id": g.operation_id})
        return jsonify({'error': 'Repeated Task not found or does not belong to this user'}), 404

    data = request.get_json()
    for key, value in data.items():
        if hasattr(repeated_task, key):
            setattr(repeated_task, key, value)
    db.session.commit()

    logger.info(f"Повторяющееся задание с ID {repeat_id} успешно обновлено", extra={"operation_id": g.operation_id})
    return jsonify({'message': 'Repeated Task updated', 'repeat_id': repeat_id})


@tasks_control_bp.route('/repeated_task/delete/<int:repeat_id>', methods=['DELETE'])
@login_required
def delete_repeated_task(repeat_id):
    user_id = current_user.user_id
    

    logger.info(f"Попытка удалить повторяющееся задание с ID {repeat_id}", extra={"operation_id": g.operation_id})

    repeated_task = RepeatingTask.query.filter_by(user_id=user_id, repeat_id=repeat_id).first()
    if repeated_task:
        repeated_tasks = Task.query.filter_by(user_id=user_id, repeated_from=repeat_id).all()
        db.session.delete(repeated_task)
        for repeated_task in repeated_tasks:
            db.session.delete(repeated_task)
        db.session.commit()
        logger.info(f"Повторяющееся задание с ID {repeat_id} успешно удалено", extra={"operation_id": g.operation_id})
        return jsonify({'message': 'Repeated Task deleted'})

    logger.error(f"Повторяющееся задание с ID {repeat_id} не найдено или не принадлежит пользователю",
                 extra={"operation_id": g.operation_id})
    return jsonify({'error': 'Repeated Task not found or does not belong to this user'}), 404


@tasks_control_bp.route('/all', methods=['GET'])
@login_required
def get_all():
    return jsonify({"message": get_all_data(current_user.user_id)}), 200


@tasks_control_bp.route('/task/<int:task_id>/subtasks', methods=['GET'])
@login_required
def get_sub_tasks(task_id):
    user_id = current_user.user_id
    task = Task.query.filter_by(user_id=user_id, task_id=task_id).first()
    if not task:
        return jsonify({'error': 'Task not found or does not belong to this user'}), 404

    subtasks = task.subtasks
    result = []
    for subtask in subtasks:
        result.append({
            'task_id': subtask.task_id,
            'title': subtask.shared_attributes.title,
            'description': subtask.shared_attributes.description
        })
    return jsonify(result)

@tasks_control_bp.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    user_id = current_user.user_id
    task = Task.query.filter_by(user_id=user_id, task_id=task_id).first()
    if not task:
        return jsonify({'error': 'Task not found or does not belong to this user'}), 404

    task_data = {
        'task_id': task.task_id,
        'title': task.shared_attributes.title,
        'description': task.shared_attributes.description,
        'priority': task.shared_attributes.priority,
        'created_at': task.created_at,
        'updated_at': task.updated_at
    }

    return jsonify(task_data)


@tasks_control_bp.route('/group/<int:group_id>/tasks', methods=['GET'])
@login_required
def get_group_tasks(group_id):
    user_id = current_user.user_id
    group = Group.query.filter_by(user_id=user_id, group_id=group_id).first()
    if not group:
        return jsonify({'error': 'Group not found or does not belong to this user'}), 404

    tasks = group.tasks
    result = []
    for task in tasks:
        result.append({
            'task_id': task.task_id,
            'title': task.shared_attributes.title,
            'description': task.shared_attributes.description
        })
    return jsonify(result)
