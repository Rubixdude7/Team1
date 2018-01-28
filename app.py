from flask import Flask, render_template
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, roles_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_user.forms import RegisterForm
from flask_mail import Mail
from wtforms import StringField, DateTimeField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model, UserMixin):

    id = db.Column('user_id', db.BigInteger, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')
    # user_dob = db.column(db.DateTime)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    # Define the Role data model


class Role(db.Model):
    id = db.Column('role_id', db.BigInteger(), primary_key=True)
    name = db.Column('role_nm', db.String(50), unique=True)

    # Define the UserRoles data model


class UserRoles(db.Model):
    id = db.Column('user_role_id', db.BigInteger(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.user_id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.role_id', ondelete='CASCADE'))


class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[DataRequired('First name is required')])
    last_name = StringField('Last name',  validators=[DataRequired('Last name is required')])
    # user_dob = DateTimeField('Date of birth', format='%Y-%m-%d %H:%M:%S')
    # TODO fix date of birth, and add 18 yr validation

# db.create_all()

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)  # Register the User model
user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm)  # Initialize Flask-User

# Needed for all pages, be sure to add as a parameter!
year = datetime.datetime.now().year


@app.route('/')
def index():

    return render_template("index.html", year=year)


@app.route('/test')
@login_required
def test():

    return render_template("test.html", year=year)


@app.route('/profile')
@login_required
def profile():

    return 'This is protected page'


@app.route('/role')
@roles_required('admin')
def role():

    return 'you have permission'


if __name__ == '__main__':
    app.run(debug=True)
