import base64
import os

from app.extensions import db
from app.models import User
from flask_bcrypt import Bcrypt
from email_validator import validate_email, EmailNotValidError

bcrypt = Bcrypt()


def generate_salt(length=16):
    """Генерирует криптографически безопасную соль.

    Args:
        length (int): Длина соли в байтах. По умолчанию 16.

    Returns:
        str: Соль в виде строки base64.
    """
    salt = os.urandom(length)  # Генерация случайных байтов
    return base64.b64encode(salt).decode('utf-8')  # Кодирование в base64 для удобства хранения


def register_user(login, email, password, name=None):
    try:
        if is_user_registered(login, email)["username_taken"]:
            return {"message": "Username already registered"}

        elif is_user_registered(login, email)["email_taken"]:
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

        print({"message": "User registered successfully", "user": repr(user)})
        return {"message": "User registered successfully", "user": repr(user)}
    except EmailNotValidError as e:
        return {"error": "Invalid email"}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def is_user_registered(username, email):
    username_exists = User.query.filter_by(login=username).first()
    email_exists = User.query.filter_by(email=email).first()
    return {
        "username_taken": bool(username_exists),
        "email_taken": bool(email_exists),
    }