import os
import dotenv

dotenv.load_dotenv()


def bool_check(value):
    return True if value=='true' else False


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = bool_check(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS'))
    DEBUG = bool_check(os.getenv('DEBUG'))
