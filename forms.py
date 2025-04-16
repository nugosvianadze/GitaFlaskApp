from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class UserUpdateForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField("Password", validators=[DataRequired(), Length(4, 20)],
                             render_kw={"class": "form-control"})
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


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
    #                                                                        FileAllowed(["jpg", "png"],
    #                                                                        "only images allowed!")])
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})

    def validate_first_name(form, field):
        if not field.data.isalpha():
            raise ValidationError("Name Must not icludes symbols")

    def validate_id_number(form, field):
        if len(str(field.data)) < 9 or len(str(field.data)) > 11:
            raise ValidationError("ID Number in incorrect, check again!")
