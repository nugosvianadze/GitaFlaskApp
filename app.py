from random import randint

from faker import Faker
from flask import Flask, render_template, url_for, redirect, request, flash, g
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from config import Config
from db_utils import get_db
from extensions import db
from forms import UserUpdateForm, SignUpForm, LoginForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
faker = Faker("ka_GE")


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100))
    address: Mapped[str]

    def __repr__(self):
        return f'{self.id} - {self.username}'

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
        db.session.commit()
        flash(f'user with id {user_id} successfully deleted!', 'success')
        return redirect(url_for('get_users'))
    flash(f'user with id {user_id} does not exists!')
    return redirect(url_for('get_users'))


@app.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    user_obj = User.query.get(user_id)
    print(user_obj)
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
        conn = get_db()
        cursor = conn.cursor()

        existing_user = cursor.execute(
            """
            select * from users where email = ?
            """,
            (form.email.data, )
        ).fetchone()

        if existing_user:
            flash(f"User with {form.email.data} already exsits!", 'danger')
            return render_template("signup.html", form=form)

        cursor.execute(
            """
            INSERT INTO users (email, password, first_name, last_name, 
            address, age, id_number, birth_date)
            VALUES (?, ?, ?,?, ?, ?, ?, ?);
            """,
            (form.email.data, form.password.data, form.first_name.data, form.last_name.data,
             form.address.data, form.age.data, form.id_number.data, form.birth_date.data)
        )
        conn.commit()
        conn.close()
        flash("You Have Successfully Signed up!", "success")
        return redirect(url_for("home"))
    return render_template("signup.html", form=form)
