import base64
import os
import uuid

from app.extensions import db
from app.models import User
from flask_bcrypt import Bcrypt
from email_validator import validate_email, EmailNotValidError
from app.extensions import logger

bcrypt = Bcrypt()


def generate_salt(length=16):
    logger.info('генерация соли длинной: ' + str(length))
    """Генерирует криптографически безопасную соль.

    Args:
        length (int): Длина соли в байтах. По умолчанию 16.

    Returns:
        str: Соль в виде строки base64.
    """
    salt = os.urandom(length)  # Генерация случайных байтов
    return base64.b64encode(salt).decode('utf-8')  # Кодирование в base64 для удобства хранения


def register_user(login, email, password, name=None, operation_id=None):
    if operation_id is None:
        operation_id = str(uuid.uuid4())

    logger.info('запрошена регистрация, логин: {}, email: {}, name: {}'.format(login, email, name),
                extra={"operation_id": operation_id})
    try:
        if is_user_registered(login, email)["username_taken"]:
            logger.info('логин уже занят', extra={"operation_id": operation_id})
            return {"message": "Username already registered"}

        elif is_user_registered(login, email)["email_taken"]:
            logger.info('почта уже занята', extra={"operation_id": operation_id})
            return {"message": "Email already registered"}



        # Валидация email
        validate_email(email)

        salt = generate_salt()

        # Хэширование пароля
        hashed_password = bcrypt.generate_password_hash(salt+password).decode('utf-8')

        # Создание нового пользователя
        user = User(login=login, email=email, password=hashed_password, name=name, salt=salt)
        db.session.add(user)
        db.session.commit()

        logger.info('Успешная регистрация логин: {}'.format(login), extra={"operation_id": operation_id})
        return {"message": "User registered successfully", "user": repr(user)}
    except EmailNotValidError as e:
        logger.error("почта не валидна", extra={"operation_id": operation_id})
        return {"error": "Invalid email"}
    except Exception as e:
        logger.error(e)
        logger.info('откат базы данных', extra={"operation_id": operation_id})
        db.session.rollback()
        return {"error": str(e)}


def is_user_registered(username, email):
    username_exists = User.query.filter_by(login=username).first()
    email_exists = User.query.filter_by(email=email).first()
    return {
        "username_taken": bool(username_exists),
        "email_taken": bool(email_exists),
    }