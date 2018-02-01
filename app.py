from flask import Flask, render_template, request, redirect, url_for
import datetime
from flask_user import login_required, roles_required, UserManager, UserMixin, current_user, user_registered
from flask_user.forms import RegisterForm
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, Form, SelectField, SubmitField
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
from data import Children #part of the dummy data. This and the other dummy data stuff can be deleted later
import models
import query

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')
Children = Children() #part of the dummy data file

mail = Mail(app)

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
db_adapter = models.PeeweeAdapter(models.db, models.user)  # Register the User model
user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm)  # Initialize Flask-User

#set up query class as db
querydb = query.query()


# new user registered
@user_registered.connect_via(app)
def _after_register_hook(sender, user, **extra):
    role = models.role.get(models.role.role_nm == 'user')
    user_role = models.user_roles(user=user, role=role)
    user_role.save()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/parent')
def parent():
    return render_template('parent.html', children=Children)


@app.route('/admin')
@roles_required('admin')
def admin():
    users = querydb.getAllUsers()
    roles = list()
    usersandroles = dict()
    for u in users:
        r = querydb.role(u.user_id)
        roles.append(r)
        usersandroles[u.email] = r
    return render_template('admin.html', users=users, roles=roles, usersandroles=usersandroles)


class RoleChangeForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


@app.route('/edit', methods=['GET', 'POST'])
@roles_required('admin')
def edit():
    form = RoleChangeForm()
    roles = querydb.getAllRoles()
    rolenames = []
    for a in roles:
        rolenames.append(a.role_nm)
    form.role.choices = [(r, r) for r in rolenames]
    if form.validate_on_submit():
        user_id = request.args.get('u_id')
        newRole = form.role.data
        querydb.updateUserRole(user_id, newRole)
        #flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    return render_template('edit.html', title='Edit Profile',
                           form=form, current_user=current_user.id)


@app.route('/delete')
def delete():
    user_id = request.args.get('u_id')
    querydb.softDeleteUser(user_id)
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
