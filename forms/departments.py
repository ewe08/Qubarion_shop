from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class DepartmentsForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = StringField('Chief id')
    members = StringField("Members")
    email = EmailField("Department Email", validators=[DataRequired()])
    submit = SubmitField('submit')
