import os
from pathlib import Path
from dotenv import load_dotenv


from flask import Flask, render_template

from app.extensions import bcrypt, db, login_manager, migrate
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.student import student_bp
from app.utils.i18n import init_i18n
from app.utils.seed import ensure_admin, seed_demo_data

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-local-launch")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    print("DB URL:", os.getenv("DATABASE_URL"))
    
    uploads_path = Path(app.instance_path) / app.config['UPLOAD_FOLDER']
    uploads_path.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    init_i18n(app)

    login_manager.localize_callback = lambda message: __import__('app.utils.i18n', fromlist=['translate']).translate(message)

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    @app.cli.command('seed-demo')
    def seed_demo_command():
        """Заполняет базу демонстрационными данными."""
        seed_demo_data()
        print('Демонстрационные данные успешно добавлены.')

    @app.errorhandler(413)
    def file_too_large(_error):
        return render_template('errors/413.html'), 413

    with app.app_context():
        ensure_admin()

    return app
