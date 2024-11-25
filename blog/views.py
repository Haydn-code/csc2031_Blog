from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy.orm import make_transient
from app import db, roles_required
from blog.forms import PostForm
from models import Post, User
from sqlalchemy import desc
import secrets

blog_blueprint = Blueprint('blog', __name__, template_folder='templates')


@blog_blueprint.route('/blog')
@login_required
@roles_required('user')
def blog():
    posts = Post.query.order_by(desc('id')).all()
    for post in posts:
        make_transient(post)
        user = User.query.filter_by(username=post.username).first()
        post.view_post(user.postkey)
    return render_template('blog/blog.html', posts=posts)


@blog_blueprint.route('/create', methods=('GET', 'POST'))
@login_required
@roles_required('user')
def create():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(username=current_user.username, title=form.title.data, body=form.body.data,
                        postkey=current_user.postkey)

        db.session.add(new_post)
        db.session.commit()

        return blog()
    return render_template('blog/create.html', form=form)


@blog_blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@roles_required('user')
def update(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        return render_template('errors/500.html')

    form = PostForm()

    if form.validate_on_submit():
        post.update_post(form.title.data, form.body.data, postkey=current_user.postkey)
        return blog()

    make_transient(post)
    post.view_post(current_user.postkey)
    form.title.data = post.title
    form.body.data = post.body

    return render_template('blog/update.html', form=form)


@blog_blueprint.route('/<int:id>/delete')
@login_required
@roles_required('user')
def delete(id):
    Post.query.filter_by(id=id).delete()
    db.session.commit()

    return blog()


@blog_blueprint.route('/filterposts')
@login_required
@roles_required('user')
def filterposts():
    posts = Post.query.filter_by(username=current_user.username).order_by(desc('id'))
    for post in posts:
        make_transient(post)
        post.view_post(current_user.postkey)

    return render_template('blog/blog.html', posts=posts)


@blog_blueprint.route('/randompost')
@roles_required('user')
def randompost():
    random_post = secrets.choice(Post.query.all())
    user = User.query.filter_by(username=random_post.username).first()
    make_transient(random_post)
    random_post.view_post(user.postkey)
    return render_template('blog/blog.html', posts=[random_post])
