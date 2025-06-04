from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField, SubmitField, ValidationError


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
