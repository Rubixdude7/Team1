from flask import Flask, render_template, request, redirect, url_for
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, roles_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user, user_registered
from flask_user.forms import RegisterForm
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, Form, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
from data import Children #part of the dummy data. This and the other dummy data stuff can be deleted later
import query

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisisasecret'
#Jason's database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mgqmsvhuvgtovyte:Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU@42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com/db42576e98688b4ab28226a87601334c89'
#Brandon's database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO make sure this is ok, this gets rid of the warning in the terminal
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')
Children = Children() #part of the dummy data file

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
    user_dob = db.column('user_dob', db.String(10))

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def is_active(self):
        return self.active


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
    first_name = StringField('First Name', validators=[DataRequired('First name is required')])
    last_name = StringField('Last Name',  validators=[DataRequired('Last name is required')])
    user_dob = StringField('Date of Birth')

    def validate_user_dob(form, field):
        born = datetime.datetime.strptime(field.data, "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if age < 18:
            raise ValidationError("We're sorry, you must be 18 or older to register")


# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, UserClass=User)  # Register the User model
user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm)  # Initialize Flask-User

#set up query class as db
db = query.query()

# new user registered
@user_registered.connect_via(app)
def _after_register_hook(sender, user, **extra):
    role = Role.query.filter_by(name="user").first()
    user_role = UserRoles(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()

@app.route('/')
def index():

    return render_template("index.html")


@app.route('/test')
@login_required
def test():

    return render_template("test.html")


@app.route('/parent')
def parent():
    return render_template('parent.html', children=Children)

@app.route('/admin')
@roles_required('admin')
def admin():
    users = db.getAllUsers()
    return render_template('admin.html', users=users)


class RoleChangeForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


@app.route('/edit', methods=['GET', 'POST'])
@roles_required('admin')
def edit():
    form = RoleChangeForm()
    roles = db.getAllRoles()
    rolenames = []
    for a in roles:
        rolenames.append(a.role_nm)
    form.role.choices = [(r, r) for r in rolenames]
    if form.validate_on_submit():
        user_id = request.args.get('u_id')
        newRole = form.role.data
        db.updateUserRole(user_id, newRole)
        #flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    return render_template('edit.html', title='Edit Profile',
                           form=form, current_user=current_user.id)


@app.route('/delete')
def delete():
    user_id = request.args.get('u_id')
    db.softDeleteUser(user_id)
    return redirect(url_for('admin'))



if __name__ == '__main__':
    app.run(debug=True)
