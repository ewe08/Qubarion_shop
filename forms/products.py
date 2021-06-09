from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):
    product = StringField("Product")
    price = StringField("Price")
    weight = StringField("Weight")
    post_picture = FileField('Add image to your post', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('submit')
