from app.extensions import bcrypt, login_manager
from app.models import User
from flask_login import current_user


def login_user_service(password, login=None, email=None):
    print(password, login, email)
    if login:
        # Ищем пользователя по логину
        user = User.query.filter_by(login=login).first()
        print(user)

    elif email:
        user = User.query.filter_by(email=email).first()

    else:
        return {"error": "No login or email provided"}

    if user:
        print()
        if bcrypt.check_password_hash(user.password, user.salt+password):
            login_user(user)
            return {"message": "Login successful"}
    return {"error": "Invalid credentials"}


@login_manager.user_loader
def login_user(user):
    return user
