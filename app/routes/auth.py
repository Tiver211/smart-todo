from flask import Blueprint, request, jsonify, redirect, url_for
from app.services.auth_service.registration_service import register_user
from app.services.auth_service.login_service import login_user_service
from app.services.auth_service.change_data import update_user_data
from app.extensions import login_manager
from flask_login import logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    return jsonify(register_user(data['login'], data['email'], data['password'], data.get('name')))


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if "login" in data and "password" in data:
        res = login_user_service(data['password'], login=data['login'])
        del res["token"]
        return jsonify(res)

    elif "email" in data and "password" in data:
        res = login_user_service(data['password'], email=data['email'])
        del res["token"]
        return jsonify(res)

    else:
        return jsonify({'error': 'No valid credentials'})


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@auth_bp.route('/change_data', methods=['POST'])
# @login_required
def change_data():
    # Получаем текущий логин пользователя
    current_login = current_user.login

    # Извлекаем данные из запроса JSON
    data = request.get_json()
    if not data:
        return jsonify({"error/message": "Не переданы данные"}), 400

    # Извлекаем параметры для обновления
    new_login = data.get('login')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')

    # Вызываем функцию обновления данных
    result = update_user_data(
        current_login=current_login,
        new_login=new_login,
        password=password,
        email=email,
        name=name
    )

    # Возвращаем результат работы функции
    return jsonify(result)
