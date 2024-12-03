from app.extensions import db, bcrypt
from app.models import User
from app.extensions import logger


def update_user_data(current_login, new_login=None, password=None, email=None, name=None, operation_id=None):
    """
    Обновляет регистрационные данные пользователя в базе данных.

    :param current_login: Текущий логин пользователя (обязательный параметр для идентификации).
    :param new_login: Новый логин (если нужно изменить).
    :param password: Новый пароль (необязательно).
    :param email: Новый email (необязательно).
    :param name: Новое имя (необязательно).
    :return: Словарь с результатом выполнения {"error/message": "<message>"}.
    """
    logger.info("выполнение смены данных пользователя: {}".format(current_login), extra={'operation_id': operation_id})
    try:
        # Проверяем, передан ли хотя бы один параметр для изменения
        if not any([new_login, password, email, name]):
            logger.info("Не указаны данные для обновления", extra={'operation_id': operation_id})
            return {"error": "Не указаны данные для обновления"}

        user = User.query.filter_by(login=current_login).first()

        # Проверяем, существует ли пользователь с текущим логином
        if not user:
            logger.info("Пользователь с таким логином не найден", extra={'operation_id': operation_id})
            return {"error": "Пользователь с таким логином не найден"}

        # Проверяем уникальность нового логина
        if new_login and new_login != current_login:
            if User.query.filter_by(login=new_login).first():
                logger.info("Логин '{}' уже занят".format(new_login), extra={'operation_id': operation_id})
                return {"error": "Логин уже занят"}
            user.login = new_login
            logger.info('Логин изменен на "{}"'.format(new_login), extra={'operation_id': operation_id})

        # Проверяем уникальность нового email
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                logger.info("почта '{}' уже занята".format(email), extra={'operation_id': operation_id})
                return {"error": "Email уже занят"}
            logger.info('почта изменена на "{}"'.format(email), extra={'operation_id': operation_id})
            user.email = email

        # Обновляем другие данные
        if password:
            password = bcrypt.generate_password_hash(user.salt+password).decode('utf-8')
            user.password = password
            logger.info('Пароль изменен на "{}"'.format(password), extra={'operation_id': operation_id})
        if name:
            user.name = name
            logger.info('Имя изменено на "{}"'.format(name), extra={'operation_id': operation_id})

        db.session.commit()
        logger.info('Данные успешно обновлены', extra={'operation_id': operation_id})
        return {"message": "Данные успешно обновлены"}
    except Exception as e:
        logger.error('ошибка обновленния данных: {}'.format(e), extra={'operation_id': operation_id})
        logger.info('откат обновлений', extra={'operation_id': operation_id})
        db.session.rollback()
        return {"error": f"Ошибка базы данных: {str(e)}"}
