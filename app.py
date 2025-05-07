import os
from random import randint

from faker import Faker
from flask import Flask, render_template, url_for, redirect, request, flash, g
from flask_migrate import Migrate
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.utils import secure_filename

from config import Config
from db_utils import get_db
from extensions import db
from forms import UserUpdateForm, SignUpForm, LoginForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
faker = Faker("ka_GE")
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100))
    address: Mapped[str]

    posts = db.relationship('Post', backref='user', cascade='all, delete', lazy=True)
    # posts = db.relationship('Post', back_populates='user', cascade='all, delete')  # need to def user
    # relation in post model

    # def __repr__(self):
    #     return f'{self.id} - {self.username}'


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url:  Mapped[str] = mapped_column(default="/test", server_default="/test")

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)

    # user = db.relationship('User', back_populates='posts', passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "user_id": self.user_id
        }


class Earth(db.Model):
    __tablename__ = 'earth'

    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    magnitude = db.Column(db.Float, nullable=False)


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
    for user_id in range(1, 51):
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
    update_form = UserUpdateForm()
    users = User.query.all()
    return render_template("users.html", user_list=users,
                           update_form=update_form)


@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id: int):
    form = UserUpdateForm()

    if form.validate_on_submit():
        username = form.data['username']
        user = User.query.get(user_id)
        if user:
            user.username = username
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
    # user_obj = User.query.filter_by(id=user_id).first()
    if not user_obj:
        print("Object Not Found")
    else:
        print(user_obj.username)
    return render_template('user_detail.html', user=user_obj)


@app.route('/user_list')
def user_list():
    return redirect(url_for('user_detail', user_id=1))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You Have Successfully Logged in!", "success")
        return redirect(url_for('home'))
    return render_template("login.html", form=form)


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
    return render_template("signup.html", form=form)


@app.route("/create_post/<int:user_id>", methods=["POST", "GET"])
def create_post(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return f"User with id : {user_id} does not exist!"

    if request.method == "GET":
        return render_template('blog/post_create.html', user_id=user_id)

    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image_url')
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


@app.route("/posts/<int:user_id>", methods=["GET"])
def posts(user_id: int):
    # get user posts with specific user_id
    user = User.query.get(user_id)

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
