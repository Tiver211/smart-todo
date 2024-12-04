from datetime import datetime

from app.extensions import db, bcrypt
from app.models import *
from app.extensions import logger


def get_all_data(user_id, operation_id=None):
    logger.info(f'запрос данных получен {user_id}', extra={'operation_id': operation_id})
    ans = []
    tasks = Task.query.filter_by(user_id=user_id, group_id=None).all()
    for task in tasks:
        ans.append(get_task_data(task))
    groups = Group.query.filter_by(user_id=user_id).all()
    for group in groups:
        ans.append(get_group_all(group.group_id))

    return ans


def get_group_all(group_id, operation_id=None):
    group = Group.query.filter_by(group_id=group_id).first()
    shared_info = SharedAttributes.query.filter_by(shared_id=group.shared_id).first()
    if not shared_info:
        return None  # Если нет связанной информации, возвращать `None`

    group_data = {
        "group_id": group.group_id,
        "user_id": group.user_id,
        "shared_info": {
            "shared_id": shared_info.shared_id,
            "title": shared_info.title,
            "description": shared_info.description,
            "priority": shared_info.priority,
            "able_to_split": shared_info.able_to_split,
            "compilable": shared_info.compilable,
            "duration": shared_info.duration.total_seconds() / 60,
            "force_time_start": shared_info.force_time_start,
            "force_end_time": shared_info.force_end_time,
            "day_period": shared_info.day_period,
            "status": shared_info.status,
        },
        "parent_id": group.parent,
        "repeated_from": group.reapeated_from,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
        "tasks": [],  # Список задач в группе
        "subgroups": []  # Список вложенных групп
    }

    # Добавляем задачи группы
    tasks = Task.query.filter_by(group_id=group.group_id).all()
    for task in tasks:
        group_data["tasks"].append(get_task_data(task))

    # Добавляем вложенные группы
    subgroups = Group.query.filter_by(parent=group.group_id).all()
    for subgroup in subgroups:
        group_data["subgroups"].append(get_group_all(subgroup))

    return group_data


def get_task_data(task):
    shared_info = SharedAttributes.query.filter_by(shared_id=task.shared_id).first()
    sub_tasks = Task.query.filter_by(parent=task.task_id).all()
    sub_tasks_data = []
    for sub_task in sub_tasks:
        sub_tasks_data.append(get_task_data(sub_task))
    task_data = {"task_id": task.task_id,
                 "user_id": task.user_id,
                 "shared_info": {"shared_id": shared_info.shared_id,
                                 "title": shared_info.title,
                                 "description": shared_info.description,
                                 "priority": shared_info.priority,
                                 "able_to_split": shared_info.able_to_split,
                                 "compilable": shared_info.compilable,
                                 "duration": shared_info.duration.total_seconds() / 60,
                                 "force_time_start": shared_info.force_time_start,
                                 "force_time_end": shared_info.force_end_time,
                                 "day_period": shared_info.day_period,
                                 "status": shared_info.status,
                                 },
                 "parent_id": task.parent,
                 "reapeated_from": task.reapeated_from,
                 "created_at": task.created_at,
                 "updated_at": task.updated_at,
                 "sub_tasks": sub_tasks_data,
                 }
    return task_data


def generate_from_reapeted_task(reapeted_task):
    shared_info = SharedAttributes.query.filter_by(shared_id=reapeted_task.shared_id).first()
    sub_tasks = RepeatingTask.query.filter_by(parent=reapeted_task.task_id).all()
    sub_tasks_data = []
    for sub_task in sub_tasks:
        sub_tasks_data.append(get_task_data(sub_task))

    sheared_task_data = {"shared_id": shared_info.shared_id,
                         "title": shared_info.title,
                         "description": shared_info.description,
                         "priority": shared_info.priority,
                         "able_to_split": shared_info.able_to_split,
                         "compilable": shared_info.compilable,
                         "duration": shared_info.duration,
                         "force_time_start": shared_info.force_time_start,
                         "force_end_time": shared_info.force_end_time,
                         "day_period": shared_info.day_period,
                         "status": shared_info.status,
                         }
    task_data = {"user_id": reapeted_task.user_id,
                 "parent_id": reapeted_task.parent,
                 "reapeted_from": reapeted_task.repeat_id,
                 "created_at": reapeted_task.created_at,
                 "updated_at": reapeted_task.updated_at,
                 "sub_tasks": sub_tasks_data,
                 }

    shared = SharedAttributes(**sheared_task_data)
    db.session.add(shared)
    db.session.commit()
    task = Task(**task_data, shared_attributes=shared.shared_id)
    db.session.add(task)
    db.session.commit()

    return get_task_data(task)
