import uuid
from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from flask_login import current_user, login_required
from app.services.tasks_control_service.tasks_control_service import *
from app.extensions import logger

tasks_control_bp = Blueprint('tasks_control', __name__, url_prefix='/tasks')


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


@tasks_control_bp.route('/get_tasks', methods=['GET'])
@login_required
def get_users_tasks():
    user_id = current_user.get_id()
    logger.info(f"Запрос на получение задач {user_id=}", extra={"operation_id": g.operation_id})
    res = get_tasks_by_user_id(user_id, g.operation_id)
    logger.info(f"Запрос задач выполнен {user_id=}", extra={"operation_id": g.operation_id})
    return res.

@login_required
@tasks_control_bp.route('/update_task', methods=['POST'])
def update_task():
    """
    Эндпоинт для обновления задачи и связанных атрибутов.
    Получает данные через JSON и вызывает функцию update_task_and_shared_attributes.
    """
    try:
        # Получение JSON-данных из запроса
        data = request.get_json()

        if not data or 'task_id' not in data:
            return jsonify({"error": "task_id is required"}), 400

        task_id = data['task_id']

        # Извлечение данных с использованием метода get() для опциональных параметров
        user_id = data.get('user_id')
        group_id = data.get('group_id')
        repeated_from = data.get('repeated_from')
        title = data.get('title')
        description = data.get('description')
        priority = data.get('priority')
        able_to_split = data.get('able_to_split')
        compilable = data.get('compilable')
        duration = data.get('duration')
        force_time_start = data.get('force_time_start')
        force_end_time = data.get('force_end_time')
        day_period = data.get('day_period')
        status = data.get('status')

        # Вызов функции обновления
        update_task_and_shared_attributes(
            task_id=task_id,
            user_id=user_id,
            group_id=group_id,
            repeated_from=repeated_from,
            title=title,
            description=description,
            priority=priority,
            able_to_split=able_to_split,
            compilable=compilable,
            duration=duration,
            force_time_start=force_time_start,
            force_end_time=force_end_time,
            day_period=day_period,
            status=status
        )

        # Возврат успешного ответа
        return jsonify({"message": "Task updated successfully."}), 200

    except ValueError as e:
        # Обработка ошибок валидации
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Обработка других ошибок
        return jsonify({"error": "An error occurred while updating the task.", "details": str(e)}), 500