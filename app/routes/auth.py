import logging
from logging.handlers import RotatingFileHandler
import uuid
from flask import Blueprint, request, jsonify, redirect, url_for
from app.services.auth_service.registration_service import register_user
from app.services.auth_service.login_service import login_user_service
from app.services.auth_service.change_data import update_user_data
from app.extensions import login_manager, logger
from flask_login import logout_user, login_required, current_user
from flask import g


# Настройка логирования
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.before_request
def assign_operation_id():
    # Генерируем уникальный идентификатор операции
    g.operation_id = str(uuid.uuid4())
    # Логируем начало обработки запроса
    logger.info(f"Начало обработки запроса {request.path}", extra={"operation_id": g.operation_id})

@auth_bp.after_request
def after_request(response):
    logger.info("Обработка запроса завершена", extra={"operation_id": g.operation_id})
    return response


@auth_bp.route('/register', methods=['POST', 'GET'])
def register():
    operation_id = g.operation_id
    data = request.json
    logger.info("Регистрация: получены данные %s", data, extra={"operation_id": operation_id})
    try:
        response = register_user(data['login'], data['email'], data['password'], data.get('name'), operation_id=operation_id)
        logger.info(response, extra={"operation_id": operation_id})
        return jsonify(response)
    except Exception as e:
        logger.error("Ошибка регистрации: %s", e, exc_info=True, extra={"operation_id": operation_id})
        return jsonify({"error": "Ошибка регистрации"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if 'login' in data:
        logger.info(f"Попытка входа: данные {data["login"]=}", extra={"operation_id": g.operation_id})
    elif 'email' in data:
        logger.info(f"Попытка входа: данные {data['email']=}", extra={"operation_id": g.operation_id})
    try:
        if "login" in data and "password" in data:
            res = login_user_service(data['password'], login=data['login'], operation_id=g.operation_id)
            logger.info("Успешный вход пользователя %s", data['login'], extra={"operation_id": g.operation_id})
            return jsonify(res), 200
        elif "email" in data and "password" in data:
            res = login_user_service(data['password'], email=data['email'], operation_id=g.operation_id)
            logger.info("Успешный вход пользователя с email %s", data['email'], extra={"operation_id": g.operation_id})
            return jsonify(res), 200
        else:
            logger.warning("Попытка входа без указания логина или email", extra={"operation_id": g.operation_id})
            return jsonify({'error': 'No valid credentials'}), 400
    except Exception as e:
        logger.error("Ошибка входа: %s", e, exc_info=True, extra={"operation_id": g.operation_id})
        return jsonify({"error": "Ошибка входа"}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logger.info("Выход пользователя %s", current_user.login, extra={"operation_id": g.operation_id})
    try:
        current_user_login = current_user.login
        logout_user()
        logger.info("Пользователь %s вышел успешно", current_user_login, extra={"operation_id": g.operation_id})
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error("Ошибка выхода: %s", e, exc_info=True, extra={"operation_id": g.operation_id})
        return jsonify({"error": "Ошибка выхода"}), 500


@auth_bp.route('/change_data', methods=['POST'])
@login_required
def change_data():
    current_login = current_user.login
    logger.info("Изменение данных для пользователя %s", current_login, extra={"operation_id": g.operation_id})

    data = request.get_json()
    if not data:
        logger.warning("Попытка изменения данных без передачи JSON", extra={"operation_id": g.operation_id})
        return jsonify({"error/message": "Не переданы данные"}), 400

    new_login = data.get('login')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')

    try:
        result = update_user_data(
            current_login=current_login,
            new_login=new_login,
            password=password,
            email=email,
            name=name,
            operation_id=g.operation_id
        )
        logger.info("Данные для пользователя %s успешно обновлены", current_login, extra={"operation_id": g.operation_id})
        return jsonify(result)
    except Exception as e:
        logger.error("Ошибка изменения данных для пользователя %s: %s", current_login, e, exc_info=True, extra={"operation_id": g.operation_id})
        return jsonify({"error": "Ошибка изменения данных"}), 500
