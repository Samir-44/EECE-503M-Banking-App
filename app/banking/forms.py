from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Email, Length


class OpenAccountForm(FlaskForm):
    type = SelectField('Type', choices=[('checking', 'Checking'), ('savings', 'Savings')], validators=[DataRequired()])
    opening_balance = DecimalField('Opening balance', places=2, default=0, validators=[NumberRange(min=0)])
    submit = SubmitField('Open Account')


class InternalTransferForm(FlaskForm):
    source_account = SelectField('Source', coerce=int, validators=[DataRequired()])
    target_account = SelectField('Target', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Description')
    submit = SubmitField('Transfer')


class ExternalTransferForm(FlaskForm):
    source_account = SelectField('Source', coerce=int, validators=[DataRequired()])
    target_account_number = StringField('Target account number', validators=[DataRequired()])
    amount = DecimalField('Amount', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Description')
    submit = SubmitField('Transfer')


class TransactionsFilterForm(FlaskForm):
    # Simple placeholder; filters via querystring in routes
    submit = SubmitField('Filter')


class EditUserForm(FlaskForm):
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=128)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField('Phone', validators=[Length(max=32)])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('support', 'Support'), ('auditor', 'Auditor'), ('admin', 'Admin')], validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Changes')
