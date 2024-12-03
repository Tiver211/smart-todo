import logging
import uuid
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache
from flask_login import LoginManager


# Создание экземпляров
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
bcrypt = Bcrypt()


class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Устанавливаем значение по умолчанию для operation_id, если оно отсутствует
        if 'operation_id' not in kwargs.get('extra', {}):
            kwargs["extra"] = kwargs.get("extra", {})
            kwargs["extra"]["operation_id"] = 'not in operation'  # Генерация нового UUID
        return msg, kwargs

def get_logger(name='main_logger', level=logging.INFO):
    log_file = f"logs\\app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    # Проверяем, существует ли уже логгер с таким именем
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Устанавливаем обработчик логов (например, в файл)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(operation_id)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


logger = get_logger()
logger = CustomLoggerAdapter(logger, {})
logger.info('all extensions created')
