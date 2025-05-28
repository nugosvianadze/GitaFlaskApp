import os

from faker import Faker
from flask import Flask, render_template, url_for, redirect, request, flash, g, session
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_alchemy import ModelForm
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from config import Config
from extensions import db
from forms import SignUpForm, LoginForm, CreatePostForm
from models import Role, User, Post, Profile
from utils import find_and_validate_user

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap4(app)

db.init_app(app)
faker = Faker("ka_GE")
migrate = Migrate(app, db)


class UserProfileForm(ModelForm):
    class Meta:
        model = Profile


def get_roles():
    return Role.query.all()


class UserUpdateForm(FlaskForm):
    # with app.app_context():
    #     roles = [(role.title, role.title) for role in Role.query.all()]
    username = StringField("User Name", validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    # roles = SelectMultipleField('Roles', choices=roles)
    roles = QuerySelectMultipleField('Roles', query_factory=get_roles)
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


# with app.app_context():
#     print('creating tables')
#     try:
#         db.create_all()
#     except Exception as e:
#         print(f'error while creating tables : {e}')
#     else:
#         print("tables creatind successfully")


@app.template_filter('remove_numbers')
def remove_numbers(s):
    final_string = ""
    for letter in s:
        if not letter.isnumeric():
            final_string += letter
    return final_string


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/home", methods=["GET"])
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route('/generate_fake_data')
def generate_fake_data():
    users = []
    for user_id in range(1, 5):
        users.append(User(email=faker.email(), username=faker.first_name() + faker.last_name(),
                          address=faker.address()))

    db.session.add_all(users)
    db.session.commit()
    return 'fake data generated successfully'


@app.route("/welcome/<user_name>", methods=["get"])
def welcome(user_name: str = ""):
    return f"Hello {user_name}"


@app.route('/users')
def get_users():
    users = User.query.all()
    return render_template("user/users.html", user_list=users)


@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id: int):
    form = UserUpdateForm()
    if form.validate_on_submit():
        roles = form.roles.data

        # roles_from_db = Role.query.filter(
        #     Role.title.in_(roles)
        # ).all()

        username = form.username.data
        user = User.query.get(user_id)
        if user:
            user.roles.clear()
            user.roles.extend(roles)
            user.username = username
            db.session.commit()
            flash(f'user successfully updated : {username}', 'success')
            return redirect(url_for('get_users'))
        flash(f'user with id {user_id} does not exist!')
        return redirect(url_for('get_users'))
    return redirect(url_for('get_users'))


@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id: int):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        flash(f'user with id {user_id} successfully deleted!', 'success')
        return redirect(url_for('get_users'))
    flash(f'user with id {user_id} does not exists!')
    return redirect(url_for('get_users'))


@app.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    user_obj = User.query.get(user_id)
    if not user_obj:
        flash('user not found', 'error')
        return redirect(url_for('get_users'))
    update_form = UserUpdateForm(data={"roles": user_obj.roles})

    # user_obj = User.query.filter_by(id=user_id).first()
    return render_template('user/user_detail.html', user=user_obj, update_form=update_form)


@app.route('/user_list')
def user_list():
    return redirect(url_for('user_detail', user_id=1))


@app.route('/login', methods=["GET", "POST"])
def login():
    if 'email' in session:
        print(session.get('email'))
        flash("You already  Logged in!", "success")

        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            flash('Invalid Credentials!')
            return render_template("user/login.html", form=form)
        session['email'] = email
        flash("You Have Successfully Logged in!", "success")
        return redirect(url_for('home'))
    return render_template("user/login.html", form=form)


@app.route('/sign-up', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        form_email = form.email.data
        existing_user = User.query.filter_by(email=form_email).first()
        # existing_user = User.query.filter(User.email == form_email).first()
        if existing_user:
            flash(f"user with email : {form_email}, already exists")
            return render_template("signup.html", form=form)
        new_user = User(
            email=form_email,
            username=form.first_name.data + " " + form.last_name.data,
            address=form.address.data
        )
        db.session.add(new_user)
        db.session.commit()

        flash("You Have Successfully Signed up!", "success")
        return redirect(url_for("home"))
    print(form.errors, form.form_errors)
    return render_template("user/signup.html", form=form)


@app.route("/create_post/<int:user_id>", methods=["POST", "GET"])
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


@app.route("/posts/<int:user_id>", methods=["GET"])
def posts(user_id: int):
    # get user posts with specific user_id
    user = User.query.get(user_id)
    print(user.profile)
    if not user:
        return "user not found"
        # flash('user not found', category="error")
        # return render_template("blog/posts.html")
    return render_template("blog/posts.html", posts=user.posts)


@app.route("/post/<int:post_id>", methods=["GET"])
def post_detail(post_id: int):
    post = Post.query.get(post_id)

    if not post:
        return f"Post with id :{post_id} does not exist!"

    return render_template("blog/post_detail.html", post=post)


@app.route('/post_delete/<int:post_id>', methods=["GET"])
def post_delete(post_id: int):
    post = Post.query.get(post_id)
    user = post.user
    if not post:
        flash(f"Post with id :{post_id} does not exist!")
        return render_template("blog/posts.html", posts=user.posts)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post with id :{post_id} successfully deleted!", 'success')
    return render_template("blog/posts.html", posts=user.posts)


@app.route('/add_roles')
def add_roles():
    test_roles = ["Admin", "Moderator", "Editor", "Viewer", "Manager", "User"]
    roles_to_add = []
    for role in test_roles:
        new_role = Role(title=role)
        roles_to_add.append(new_role)

    db.session.add_all(roles_to_add)
    db.session.commit()
    return "roles successfully added"


@app.route('/create_profile/<int:user_id>', methods=["GET", "POST"])
def create_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user, user_id)

    form = UserProfileForm()
    if request.method == "POST":
        if form.validate():
            bio = request.form.get('bio')
            # profile = Profile(bio=form.bio.data,
            #                   user_id=user_id)
            # db.session.add(profile)
            # db.session.commit()
            profile = Profile(bio=bio)
            user.profile = profile
            db.session.commit()
            flash('Profile Successfully Created!', 'success')
            return redirect(url_for('user_profile', user_id=user_id))
    return render_template('user/create_profile.html',
                           form=form, user=user)


@app.route('/user_profile/<int:user_id>')
def user_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user, user_id)
    return render_template("user/profile.html", user=user)


@app.route('/update_profile/<int:user_id>', methods=["POST", "GET"])
def update_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user, user_id)
    form = UserProfileForm(data={'bio': user.profile.bio})

    if request.method == 'POST':
        if form.validate():
            bio = request.form.get('bio')
            user.profile.bio = bio
            db.session.commit()
            flash('Profile Successfully Updated!', 'success')
            return redirect(url_for('user_profile', user_id=user_id))

    return render_template('user/edit_profile.html', form=form, user=user)


@app.route('/delete_profile/<int:user_id>')
def delete_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user, user_id)
    if not user.profile:
        flash("User does not have profile")
        return redirect(url_for('get_users'))
    # db.session.delete(user.profile)
    user.profile = None
    db.session.commit()
    flash(f"user {user.username}'s profile successfully deleted!", "success")
    return redirect(url_for('user_profile', user_id=user_id))


@app.route('/sign_out')
def sign_out():
    email = session.pop('email')
    flash(f"user {email} succ logged out!", "success")
    return redirect(url_for('login'))