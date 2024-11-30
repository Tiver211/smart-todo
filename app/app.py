import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # Получение значения переменной окружения

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_value')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
