# ELMS/my_flask_app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from my_flask_app.models import User, LeaveRequest, Role # Import models to check for uniqueness

class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """Custom validator to check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """Custom validator to check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class LeaveApplicationForm(FlaskForm):
    """Form for employees to apply for leave."""
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    reason = TextAreaField('Reason for Leave',
                           validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Apply for Leave')

    def validate_end_date(self, field):
        """Custom validator to ensure end date is not before start date."""
        if field.data < self.start_date.data:
            raise ValidationError('End date cannot be before start date.')

class UserUpdateForm(FlaskForm):
    """Form for admin to update user details and roles."""
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    role = SelectField('Role', coerce=int, validators=[DataRequired()]) # coerce=int to convert value to integer
    is_active = BooleanField('Account Active')
    submit = SubmitField('Update User')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        # Populate roles dynamically
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]

    def validate_username(self, username):
        """Custom validator to check for username uniqueness during update."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """Custom validator to check for email uniqueness during update."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PasswordResetForm(FlaskForm):
    """Basic form for password reset (for admin to reset user passwords)."""
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password',
                                         validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')

class LeaveActionForm(FlaskForm):
    """Form for managers to approve/reject leave requests."""
    status = SelectField('Action', choices=[('Approved', 'Approve'), ('Rejected', 'Reject')], validators=[DataRequired()])
    manager_notes = TextAreaField('Manager Notes (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Submit Action')
