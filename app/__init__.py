from flask import Flask
from app.extensions import db, migrate
from app.config import Config
from app.flask_app import create_app

