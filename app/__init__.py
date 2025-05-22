from flask_socketio import SocketIO

from flask import Flask
socketio = SocketIO()
def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    socketio.init_app(app)
    return app


