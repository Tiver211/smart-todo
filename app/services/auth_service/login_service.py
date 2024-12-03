from app.extensions import bcrypt, login_manager
from app.models import User
from flask_login import current_user, login_user, confirm_login
from app.extensions import logger


def login_user_service(password, login=None, email=None, operation_id=None):
    logger.info('Запрос на вход логин: {}, почта: {}'.format(login, email), extra={'operation_id': operation_id})
    if login:
        logger.info('вход по логину', extra={'operation_id': operation_id})
        # Ищем пользователя по логину
        user = User.query.filter_by(login=login).first()

    elif email:
        logger.info('вход по почте', extra={'operation_id': operation_id})
        user = User.query.filter_by(email=email).first()

    else:
        logger.warning('данные для входа не переданы', extra={'operation_id': operation_id})
        return {"error": "No login or email provided"}

    if user:
        if bcrypt.check_password_hash(user.password, user.salt+password):
            login_user(user, remember=True)
            logger.info('вход успешен', extra={'operation_id': operation_id})
            return {"message": "Login successful"}
    logger.info('неверные логин или пароль', extra={'operation_id': operation_id})
    return {"error": "Invalid credentials"}


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()
