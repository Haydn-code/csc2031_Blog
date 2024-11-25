from flask import Blueprint, render_template
from flask_login import login_required
from models import User
from app import roles_required


admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/admin')
@login_required
@roles_required('admin')
def admin():
    return render_template('admin/admin.html')


@admin_blueprint.route('/view_all_users', methods=['POST'])
@login_required
@roles_required('admin')
def view_all_users():
    return render_template('admin/admin.html', current_users=User.query.all())


@admin_blueprint.route('/logs', methods=['POST'])
@login_required
@roles_required('admin')
def logs():
    with open("blog.log", "r") as f:
        content = f.read().splitlines()[-10:]

    return render_template('admin/admin.html', logs=content)