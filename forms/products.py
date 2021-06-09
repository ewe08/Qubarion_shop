from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField


class ProductForm(FlaskForm):
    product = StringField("Product")
    price = StringField("Price")
    weight = StringField("Weight")
    post_picture = FileField('Add image to your post')
    submit = SubmitField('submit')
