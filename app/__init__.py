from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(async_mode='eventlet')  # Указываем async_mode здесь

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    socketio.init_app(app)  # Просто инициализируем

    return app
