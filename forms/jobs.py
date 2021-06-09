from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader = StringField('Team leader id')
    work_size = StringField("Work size")
    collaborators = StringField("collaborators")
    is_finished = BooleanField("Is job finished?")
    submit = SubmitField('submit')
