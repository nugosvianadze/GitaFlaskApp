import sqlite3

from flask import Flask, render_template, url_for, redirect, request, flash, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, PasswordField, SubmitField, FileField, StringField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

app = Flask(__name__)
DATABASE = "my_first_db.sqlite3"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.config["SECRET_KEY"] = 'aasdasdasdasd87123817231h287h8712bsy1vyv1st1vsfy xasdtqweqwed'


users = [
    {"id": 1, "name": "Joh2n Do1e", "email": "johndoe@example.com"},
    {"id": 2, "name": "Jane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane SmithJane Smith", "email": "janesmith@example.com"},
    {"id": 3, "name": "Alice Johnson", "email": "alicejohnson@example.com"},
    {"id": 4, "name": "Bob Brown", "email": "bobbrown@example.com"},
    {"id": 5, "name": "Charlie Davis", "email": "charliedavis@example.com"},
    {"id": 6, "name": "David Wilson", "email": "davidwilson@example.com"},
    {"id": 7, "name": "Eve Taylor", "email": "evetaylor@example.com"},
    {"id": 8, "name": "Frank Moore", "email": "frankmoore@example.com"},
    {"id": 9, "name": "Grace Lee", "email": "gracelee@example.com"},
    {"id": 10, "name": "Hannah Clark", "email": "hannahclark@example.com"}
]


@app.route("/home", methods=["GET"])
@app.route("/", methods=["GET"])
def home():

    return render_template("home.html")


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

    return render_template("users.html", user_list=users)


@app.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    user_obj = None
    for user in users:
        if user['id'] == user_id:
            user_obj = user
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

        # form.data.pop('submit')
        # form.data.pop('confirm_password')
        # form.data.pop('csrf_token')
        # print(form.data.values())
        # values = form.data.values()
        # print(*values)
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
        # conn.close()
        flash("You Have Successfully Signed up!", "success")
        return render_template("signup.html", form=form)
    return render_template("signup.html", form=form)
