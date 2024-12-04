from datetime import datetime

from app.extensions import db, bcrypt
from app.models import Task, RepeatingTask, SharedAttributes
from app.extensions import logger


def get_tasks_by_user_id(user_id, operation_id=None, ):
    logger.info(f'Выполнение поиска задач пользователя {user_id=}', extra={'operation_id': operation_id})

    res = Task.query.filter_by(user_id=user_id).all()

    logger.info("Поиск выполнен", extra={'operation_id': operation_id})
    return res


def create_task(user_id,
                title,
                description,
                priority,
                able_to_split,
                duration,
                compiliable,
                force_time_start=None,
                force_time_end=None,
                day_period=None,
                parent=None,
                group_id=None,
                reapeted_from=None,
                operation_id=None,):
    logger.info("Добавление задачи", extra={'operation_id': operation_id})
    try:
        shared = SharedAttributes(
            title=title,
            description=description,
            priority=priority,
            able_to_split=able_to_split,
            compiliable=compiliable,
            duration=duration,
            force_time_start=force_time_start,
            force_time_end=force_time_end,
            day_period=day_period
        )
        db.session.add(shared)

        task = Task(
            user_id=user_id,
            shared_id=shared.shared_id,
            parent_id=parent.id,
            group_id=group_id,
            reapeted_from=reapeted_from,
        )

        db.session.add(task)
        logger.info('Задача создана', extra={'operation_id': operation_id})

    except Exception as e:
        db.session.rollback()
        logger.error(f'ошибка {e} при создании задачи', extra={'operation_id': operation_id})
        return {'error': str(e)}


def delete_task(task_id, operation_id=None):
    try:
        logger.info(f'Удаление задачи {task_id}', extra={'operation_id': operation_id})
        task = Task.query.filter_by(id=task_id).first()
        db.session.delete(task)
        db.session.commit()
        logger.info('Задача удалена', extra={'operation_id': operation_id})

    except Exception as e:
        db.session.rollback()
        logger.error('ошибка при удалении задачи', extra={'operation_id': operation_id})
        return {'error': str(e)}


def update_task_and_shared_attributes(
        task_id,
        user_id=None,
        group_id=None,
        repeated_from=None,
        title=None,
        description=None,
        priority=None,
        able_to_split=None,
        compilable=None,
        duration=None,
        force_time_start=None,
        force_end_time=None,
        day_period=None,
        status=None,
        operation_id=None,
):
    """
    Обновляет данные задачи (Task) и связанные с ней общие атрибуты (SharedAttributes).

    :param task_id: ID задачи, которую необходимо обновить.
    :param user_id: Новый user_id для задачи (опционально).
    :param group_id: Новый group_id для задачи (опционально).
    :param repeated_from: Новый repeated_from для задачи (опционально).
    :param title: Новое название в SharedAttributes (опционально).
    :param description: Новое описание в SharedAttributes (опционально).
    :param priority: Новый приоритет в SharedAttributes (опционально).
    :param able_to_split: Новое значение флага "можно разделить" (опционально).
    :param compilable: Новое значение флага "можно компилировать" (опционально).
    :param duration: Новая продолжительность в SharedAttributes (опционально).
    :param force_time_start: Новое принудительное время начала (опционально).
    :param force_end_time: Новое принудительное время окончания (опционально).
    :param day_period: Новый период дня (опционально).
    :param status: Новый статус (опционально).
    """
    logger.info(f'обновления данных задания {user_id}', extra={'operation_id': operation_id})
    # Найти задачу по ID
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        logger.error('Такого задания не существует', extra={'operation_id': operation_id})
        return {"error": f"Task with ID {task_id} not found."}

    if task.user_id != user_id:
        return {"error": f"User id {user_id} not correct."}

    # Обновить данные задачи (Task)
    if user_id is not None:
        task.user_id = user_id
    if group_id is not None:
        task.group_id = group_id
    if repeated_from is not None:
        task.repeated_from = repeated_from
    task.updated_at = datetime.now()

    # Обновить данные общих атрибутов (SharedAttributes)
    shared_attributes = task.shared_attributes
    if not shared_attributes:
        raise ValueError(f"SharedAttributes for task ID {task_id} not found.")

    if title is not None:
        shared_attributes.title = title
    if description is not None:
        shared_attributes.description = description
    if priority is not None:
        shared_attributes.priority = priority
    if able_to_split is not None:
        shared_attributes.able_to_split = able_to_split
    if compilable is not None:
        shared_attributes.compilable = compilable
    if duration is not None:
        shared_attributes.duration = duration
    if force_time_start is not None:
        shared_attributes.force_time_start = force_time_start
    if force_end_time is not None:
        shared_attributes.force_end_time = force_end_time
    if day_period is not None:
        shared_attributes.day_period = day_period
    if status is not None:
        shared_attributes.status = status
    shared_attributes.updated_at = datetime.now()

    # Сохранение изменений
    db.session.commit()