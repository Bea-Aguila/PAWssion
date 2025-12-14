from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, URL
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Login
class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()])
    
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)])

    submit = SubmitField(
        "Login",
        render_kw={"class": "submit-btn"})

# User Registration
class UserRegisterForm(FlaskForm):
    first_name = StringField(
        "First Name", 
        validators=[DataRequired()])
    
    last_name = StringField(
        "Last Name", 
        validators=[DataRequired()])

    username = StringField(
        "Username", 
        validators=[DataRequired()])
    
    email = StringField(
        "Email", 
        validators=[DataRequired(), Email()])
    
    password = PasswordField(
        "Password", 
        validators=[DataRequired(), Length(min=8)])

    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[DataRequired(),
        EqualTo('password', 
        message='Passwords must match!')])
    
    submit = SubmitField(
        "Register", 
        render_kw={"class": "submit-btn"})

# Shelter Registration
class ShelterRegisterForm(FlaskForm):
    name = StringField(
        "Shelter Name", 
        validators=[DataRequired()])
    
    description = TextAreaField(
        "Shelter Description", 
        validators=[DataRequired()],
        render_kw={"placeholder": "Describe your shelter and its mission for others to see…"})
    
    address = StringField(
        "Address", 
        validators=[DataRequired()])
    
    contact_number = StringField(
        "Contact Number", 
        validators=[DataRequired(), Length(min=11, max=11, message='Invalid Contact number')])
    
    email = StringField(
        "Email", 
        validators=[DataRequired(), Email()])
    
    website = StringField(
        'Website',
        validators=[Optional(), URL(message="Please enter a valid URL (include http:// or https://)")])
    
    date_established = StringField(
        "Date Established (Month/Year)", 
        validators=[DataRequired(), Length(min=7, max=7)],
        render_kw={"placeholder": "09/2002"})
    
    shelter_type = SelectField(
        "Type of Shelter", 
        choices=[('Private','Private'),
                 ('Government','Government'),
                 ('Non-Profit','Non-Profit')])
    
    password = PasswordField(
        "Password", 
        validators=[DataRequired(), Length(min=8)])
    
    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[DataRequired(),
        EqualTo('password', 
        message='Passwords must match!')])

    
    declaration = BooleanField(
        "I certify that the information above is correct", 
        validators=[DataRequired()], render_kw={"class": "declaration-checkbox"})
    
    submit = SubmitField(
        "Register", 
        render_kw={"class": "submit-btn"})

# Animal Form
class AnimalForm(FlaskForm):
    type = SelectField("Type", 
        choices=[("Dog","Dog"),
                 ("Cat","Cat")], 
        validators=[DataRequired()])

    breed = StringField(
        "Breed", 
        validators=[DataRequired()])

    gender = SelectField(
        "Gender", 
        choices=[("Male","Male"),
                 ("Female","Female")], 
        validators=[DataRequired()])

    name = StringField(
        "Name", 
        validators=[DataRequired()])

    age = IntegerField(
        "Age", 
        validators=[Optional(),NumberRange(min=0, message="Must be 0 or greater")])
    
    description = TextAreaField(
        "Description", 
        validators=[DataRequired()])

    image1 = FileField(
        "Image", validators=[DataRequired(),
        FileRequired(message="Image is required."),
        FileAllowed(["jpg","jpeg","png"], "Images only!")])

    submit = SubmitField(
        "Submit",
        render_kw={"class": "submit-btn"})
    
# Adoption Form
class AdoptionForm(FlaskForm):
    # Hidden fields
    animal_id = HiddenField(validators=[DataRequired()])
    shelter_id = HiddenField(validators=[DataRequired()])

    # User information
    
    address = StringField(
        "Applicant Address", 
        validators=[DataRequired()])
    
    contact = StringField(
        "Applicant Contact Number", 
        validators=[DataRequired(), Length(min=11, max=11)])
    
    gender = SelectField(
        "Applicant Gender", 
        choices=[('Male', 'Male'), 
                 ('Female', 'Female')], 
        validators=[DataRequired()])
    
    age = IntegerField(
        "Applicant Age", 
        validators=[DataRequired(),
        NumberRange(min=18, message="Must be 18 years old and above")])
    
    reason = TextAreaField(
        "Reason for Adoption", 
        validators=[DataRequired()])

    # Submit button
    submit = SubmitField(
        "Submit Adoption Request",
        render_kw={"class": "submit-btn"})
    

class UserInfoForm(FlaskForm):
    first_name = StringField(
        "First Name", validators=[DataRequired()])
    
    last_name = StringField(
        "Last Name", validators=[DataRequired()])
    
    username = StringField(
        "Username", validators=[DataRequired()])
    
    email = StringField(
        "Email", validators=[DataRequired(), Email()])
    
    age = IntegerField(
        "Age", validators=[Optional(), NumberRange(min=18)])
    
    gender = SelectField(
        "Gender", choices=[('Male', 'Male'), ('Female', 'Female')], 
        validators=[Optional()])
    
    address = StringField(
        "Address", validators=[Optional()])
    
    contact = StringField("" \
    "Contact Number", validators=[Optional(), Length(min=11, max=11)])
    
    submit = SubmitField(
        "Save Information",
        render_kw={"class": "submit-btn"})
