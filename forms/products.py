from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField


class ProductForm(FlaskForm):
    product = StringField("Product")
    price = StringField("Price")
    weight = StringField("Weight")
    post_picture = FileField('Profile Picture', validators=[FileAllowed([
        'jpg', 'png'])])
    submit = SubmitField('submit')
