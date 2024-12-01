from flask import Flask
from app.extensions import db, migrate, login_manager, mail, cache, bcrypt
from app.models import User, Task, Group  # Импортируйте ваши модели


def create_app(name=None):
    print('starting app')
    if name:
        app = Flask(name)

    else:
        app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_object('app.config.Config')

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    # cache.init_app(app)

    # Регистрация маршрутов
    from app.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app

