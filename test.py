from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)

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
    email = EmailField("Email", validators=[DataRequired()], render_kw={"class": "form-control"})
    password = PasswordField("Password", validators=[DataRequired(), Length(4, 20)],
                             render_kw={"class": "form-control"})
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    form.validate_on_submit()
    return render_template("login.html", form=form)


@app.route('/sign-up', methods=["GET", "POST"])
def signup():
    return render_template("signup.html")
