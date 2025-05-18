from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, EmailField, PasswordField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    password = PasswordField("Password", validators=[DataRequired(), Length(4, 20)],
                             render_kw={"class": "form-control"})
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})


class SignUpForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    # password = PasswordField("Password", validators=[DataRequired(), Length(4, 20),
    #                                                  EqualTo('confirm_password',
    #                                                          message='Passwords must match')],
    #                          render_kw={"class": "form-control"})
    # confirm_password = PasswordField('Repeat Password', render_kw={"class": "form-control"})
    first_name = StringField("First Name", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    last_name = StringField("Last Name", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    address = StringField("Address", validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    # age = IntegerField("Age", validators=[DataRequired()],
    #                          render_kw={"class": "form-control"})
    # id_number = IntegerField("ID Number", validators=[DataRequired()],
    #                          render_kw={"class": "form-control"})
    # birth_date = DateField("Birth Date", validators=[DataRequired()],
    #                        render_kw={"class": "form-control"})

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


class CreatePostForm(FlaskForm):
    title = StringField("Title", render_kw={"class": "form-control"})
    description = TextAreaField("Description", render_kw={"class": "form-control"})
    image_url = FileField("Image Url", validators=[FileAllowed(['jpg', 'png', 'gif', 'webp'],
                                                               'Images only!')])
    submit = SubmitField(render_kw={"class": "btn btn-primary w-100"})

    # def validate(self, extra_validators=None):
    #     image = self.data.get('image_url').read()
    #     title, description = self.data.get('title'), self.data.get('description')
    #     fields = [title, image, description]
    #     if not any(fields):
    #         # self.errors["field_validation"] = "u must provide one field"
    #         raise ValidationError("u must provide one field")

    def validate_description(self, title):
        if not title.data:
            raise ValidationError("Provide Description!")
