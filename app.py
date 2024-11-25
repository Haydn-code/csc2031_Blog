from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager, current_user
from functools import wraps
from flask_talisman import Talisman
import logging
import os


class SecurityFilter(logging.Filter):
    def filter(self, record):
        return 'SECURITY' in record.getMessage()


logger = logging.getLogger()
file_handler = logging.FileHandler('blog.log', 'a')
file_handler.setLevel(logging.WARNING)
file_handler.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQLALCHEMY_ECHO') == 'True'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')
db = SQLAlchemy(app)

csp = {
    'default-src': ['\'self\'', 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'],
    'frame-src': ['\'self\'', 'https://www.google.com/recaptcha/', 'https://recaptcha.google.com/recaptcha/'],
    'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://www.google.com/recaptcha/',
                   'https://www.gstatic.com/recaptcha/']
}

talisman = Talisman(app, content_security_policy=csp)


def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('errors/403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


@app.errorhandler(403)
def forbidden_error(error):
    logging.warning('SECURITY - Unauthorised Access Attempts [%s, %s, %s, %s]', current_user.id, current_user.username
                    , current_user.role, request.remote_addr)
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


from main.views import main_blueprint
from blog.views import blog_blueprint
from users.views import users_blueprint
from admin.views import admin_blueprint
from models import User

app.register_blueprint(main_blueprint)
app.register_blueprint(blog_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


if __name__ == '__main__':
    app.run()
