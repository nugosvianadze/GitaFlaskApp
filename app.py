import sqlite3
from random import randint

from faker import Faker
from flask import Flask, render_template, url_for, redirect, request, flash, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, PasswordField, SubmitField, FileField, StringField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

app = Flask(__name__)
DATABASE = "my_first_db.sqlite3"
faker = Faker("ka_GE")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.config["SECRET_KEY"] = 'aasdasdasdasd87123817231h287h8712bsy1vyv1st1vsfy xasdtqweqwed'


@app.route("/home", methods=["GET"])
@app.route("/", methods=["GET"])
def home():

    return render_template("home.html")


@app.route('/generate_fake_data')
def generate_fake_data():
    conn = get_db()
    cursor = conn.cursor()

    for user_id in range(1, 51):
        cursor.execute(
            """
            INSERT INTO users (email, password, first_name, last_name, 
            address, age, id_number, birth_date)
            VALUES (?, ?, ?,?, ?, ?, ?, ?);
            """,
            (faker.email(), faker.password(), faker.first_name(), faker.last_name(),
             faker.address(), randint(1, 100), randint(100000000, 99999999999),
             faker.date())
        )
    conn.commit()
    conn.close()
    return 'fake data generated successfully'



@app.route("/welcome/<user_name>", methods=["get"])
def welcome(user_name: str = ""):
    return f"Hello {user_name}"


@app.route("/students/list")
def students_list():
    student_list = [
        "Nugo", "Giorgi", "Mariami",
        "Nugo", "Giorgi", "Mariami",
        "Nugo", "Giorgi", "Mariami",
    ]

    return render_template("students.html", students=student_list)


@app.route('/users')
def get_users():
    conn = get_db()
    cursor = conn.cursor()

    users = cursor.execute(
        """
        select * from users
        """
    ).fetchall()
    conn.close()
    return render_template("users.html", user_list=users)


@app.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    conn = get_db()
    cursor = conn.cursor()

    user_obj = cursor.execute("""
    select * from users where id = ?
    """,
        (user_id, )).fetchone()
    conn.close()
    return render_template('user_detail.html', user=user_obj)


@app.route('/user_list')
def user_list():
    return redirect(url_for('user_detail', user_id=1))


@app.template_filter('remove_numbers')
def remove_numbers(s):
    print(s)
    final_string = ""
    for letter in s:
        if not letter.isnumeric():
            final_string += letter
    print(f"final string : {final_string}")
    return final_string


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField("Password", validators=[DataRequired(), Length(4, 20)],
                             render_kw={"class": "form-control"})
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You Have Successfully Logged in!", "success")
        return redirect(url_for('home'))
    return render_template("login.html", form=form)


class SignUpForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField("Password", validators=[DataRequired(), Length(4, 20),
                                                     EqualTo('confirm_password',
                                                             message='Passwords must match')],
                             render_kw={"class": "form-control"})
    confirm_password = PasswordField('Repeat Password', render_kw={"class": "form-control"})
    first_name = StringField("First Name", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    last_name = StringField("Last Name", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    address = StringField("Address", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    age = IntegerField("Age", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    id_number = IntegerField("ID Number", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    birth_date = DateField("Birth Date", validators=[DataRequired()],
                           render_kw={"class": "form-control"})

    # profile_picture = FileField("Upload Your Profile Picture", validators=[DataRequired(),
    #                                                                        FileAllowed(["jpg", "png"], "only images allowed!")])
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})

    def validate_first_name(form, field):
        if not field.data.isalpha():
            raise ValidationError("Name Must not icludes symbols")

    def validate_id_number(form, field):
        if len(str(field.data)) < 9 or len(str(field.data)) > 11:
            raise ValidationError("ID Number in incorrect, check again!")


@app.route('/sign-up', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    print(form.validate_on_submit())
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
