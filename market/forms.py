from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf.file import FileRequired
from market.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username = username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists. Please try a new username.')
        
    def validate_email_address(self, email_address_to_check):
        email = User.query.filter_by(email_address = email_address_to_check.data).first()
        if email:
            raise ValidationError('Email is already registered.')
    
    def validate_mobile(self, mobile_to_check):
        mobile = User.query.filter_by(mobile = mobile_to_check.data).first()
        if mobile:
            raise ValidationError('Mobile number is already registered.')

    username = StringField(label = 'Username', validators=[Length(min=2, max=30), DataRequired()])
    name = StringField(label = 'Name', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label = 'Email Address', validators=[Email(), DataRequired()])
    mobile = StringField(label = 'Mobile Number', validators=[Length(10), DataRequired()])
    password1 = PasswordField(label = 'Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label = 'Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label = 'Create Account')

class LoginForm(FlaskForm):
    username = StringField(label = 'Username', validators=[DataRequired()])
    password = PasswordField(label = 'Password', validators=[DataRequired()])
    submit = SubmitField(label = 'Login')

class SellerForm(FlaskForm):
    name = StringField(label = 'Name')
    aadhar = StringField(label = 'Aadhar Number', validators=[DataRequired(), Length(12)])
    image = FileField(label = 'Profile picture', validators=[FileRequired()])
    submit = SubmitField(label = 'Apply')

class ItemForm(FlaskForm):
    name = StringField(label = 'Item name', validators=[DataRequired()])
    price = StringField(label = 'Price', validators=[DataRequired()])
    description = StringField(label = 'Item description', validators=[DataRequired()])
    image = FileField(label = 'Item image', validators=[FileRequired()])
    submit = SubmitField(label = 'Submit')

class AddressForm(FlaskForm):
    line1 = StringField(label = 'Line 1', validators=[DataRequired()])
    line2 = StringField(label = 'Line 2', validators=[DataRequired()])
    landmark = StringField(label = 'Landmark')
    city = StringField(label = 'City', validators=[DataRequired()])
    state = StringField(label = 'State', validators=[DataRequired()])
    country = StringField(label = 'Country', validators=[DataRequired()])
    pincode = StringField(label = 'Pincode', validators=[DataRequired()])
    submit = SubmitField(label = 'Submit')
