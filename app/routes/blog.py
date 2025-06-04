import os

from flask import render_template, redirect, Blueprint, session, url_for, flash
from werkzeug.utils import secure_filename

from app.extensions import db
from app.forms.post import CreatePostForm
from app.models.post import Post
from app.models.user import Role, User

blog_bp = Blueprint("blog", __name__, template_folder='blog', url_prefix='/blog')


@blog_bp.route('/add_roles')
def add_roles():
    test_roles = ["Admin", "Moderator", "Editor", "Viewer", "Manager", "User"]
    roles_to_add = []
    for role in test_roles:
        new_role = Role(title=role)
        roles_to_add.append(new_role)

    db.session.add_all(roles_to_add)
    db.session.commit()
    return "roles successfully added"


@blog_bp.route("/create_post/<int:user_id>", methods=["POST", "GET"])
def create_post(user_id: int):
    form = CreatePostForm()
    user = User.query.get(user_id)
    if not user:
        return f"User with id : {user_id} does not exist!"

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        image = form.image_url.data
        filename = secure_filename(image.filename)

        if image:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_post = Post(
            title=title,
            description=description,
            image_url=os.path.join(app.config['UPLOAD_FOLDER'], filename) if image else None,
            user_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('post created successfully', 'success')
        return redirect(url_for('post_detail', post_id=new_post.id))

    return render_template('blog/post_create.html', user_id=user_id, form=form)


@blog_bp.route("/posts/<int:user_id>", methods=["GET"])
def posts(user_id: int):
    # get user posts with specific user_id
    user = User.query.get(user_id)
    print(user.profile)
    if not user:
        return "user not found"
        # flash('user not found', category="error")
        # return render_template("blog/posts.html")
    return render_template("blog/posts.html", posts=user.posts)


@blog_bp.route("/post/<int:post_id>", methods=["GET"])
def post_detail(post_id: int):
    post = Post.query.get(post_id)

    if not post:
        return f"Post with id :{post_id} does not exist!"

    return render_template("blog/post_detail.html", post=post)


@blog_bp.route('/post_delete/<int:post_id>', methods=["GET"])
def post_delete(post_id: int):

    if 'email' not in session:
        return redirect(url_for('login'))
    email = session.get('email')

    post = Post.query.get(post_id)

    if not post:
        return redirect(url_for('my_profile'))

    user = post.user

    if user.email != email:
        flash('You are not allowed to do this action!')
        return redirect(url_for('my_profile'))

    if not post:
        flash(f"Post with id :{post_id} does not exist!")
        return render_template("blog/posts.html", posts=user.posts)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post with id :{post_id} successfully deleted!", 'success')
    return redirect(url_for('my_profile'))

@blog_bp.route("/home", methods=["GET"])
@blog_bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")
