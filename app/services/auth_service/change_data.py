from app.extensions import db, bcrypt
from app.models import User


def update_user_data(current_login, new_login=None, password=None, email=None, name=None):
    """
    Обновляет регистрационные данные пользователя в базе данных.

    :param current_login: Текущий логин пользователя (обязательный параметр для идентификации).
    :param new_login: Новый логин (если нужно изменить).
    :param password: Новый пароль (необязательно).
    :param email: Новый email (необязательно).
    :param name: Новое имя (необязательно).
    :return: Словарь с результатом выполнения {"error/message": "<message>"}.
    """
    try:
        # Проверяем, передан ли хотя бы один параметр для изменения
        if not any([new_login, password, email, name]):
            return {"error": "Не указаны данные для обновления"}

        user = User.query.filter_by(login=current_login).first()

        # Проверяем, существует ли пользователь с текущим логином
        if not user:
            return {"error": "Пользователь с таким логином не найден"}

        # Проверяем уникальность нового логина
        if new_login and new_login != current_login:
            if User.query.filter_by(login=new_login).first():
                return {"error": "Логин уже занят"}
            user.login = new_login

        # Проверяем уникальность нового email
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return {"error": "Email уже занят"}
            user.email = email

        # Обновляем другие данные
        if password:
            password = bcrypt.generate_password_hash(user.salt+password).decode('utf-8')
            user.password = password
        if name:
            user.name = name

        db.session.commit()
        return {"error/message": "Данные успешно обновлены"}
    except Exception as e:
        db.session.rollback()
        return {"error": f"Ошибка базы данных: {str(e)}"}
