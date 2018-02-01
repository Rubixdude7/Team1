from flask import Flask, render_template, request, redirect, url_for
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_user import login_required, roles_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user
from flask_user import login_required, roles_required, UserManager, UserMixin, SQLAlchemyAdapter, current_user, \
    user_registered
from flask_user.forms import RegisterForm
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, Form, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect, url_for
from models import *
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
from data import Children  # part of the dummy data. This and the other dummy data stuff can be deleted later
import query
from flask import flash, render_template, request, redirect

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisisasecret'
# my doesnt work
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vnqimdibqlqhqgap:pdCJFgqiUjR68iGphryN5g6sdHEf3Voi7WQYPHvTpCFuyxdE3xkvYuQhgkF6Hjo8@38b32831-bc8a-4cf6-acef-a878003849f7.sqlserver.sequelizer.com/db38b32831bc8a4cf6acefa878003849f7'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
# Jason's database
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mgqmsvhuvgtovyte:Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU@42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com/db42576e98688b4ab28226a87601334c89'
# Brandon's database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO make sure this is ok, this gets rid of the warning in the terminal
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')
Children = Children()  # part of the dummy data file

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
    last_name = StringField('Last Name', validators=[DataRequired('Last name is required')])
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

# set up query class as db
querydb = query.query()


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


@app.route('/editQuestion', methods=['GET', 'POST'])
def editQuestion():
    q_id = request.args.get('q_id')
    getQuestion = querydb.getQuestion(q_id)
    form = QuestionEdit(request.form)
    if form.validate_on_submit():
        newQuestion = form.question.data
        querydb.editQuestion(q_id, newQuestion)
        # flash('Your changes have been saved.')
        return redirect(url_for('questions'))
    return render_template('editQuestion.html', title='Edit Question',
                           form=form, current_user=current_user.id, question=getQuestion)


@app.route('/questiondeactivate')
def questiondeactivate():
    q_id = request.args.get('q_id')
    querydb.deactivateQuestion(q_id)
    return redirect(url_for('questions'))


@app.route('/questionreactivate')
def questionreactivate():
    q_id = request.args.get('q_id')
    querydb.reactivateQuestion(q_id)
    return redirect(url_for('questions'))


@app.route('/questionDelete')
def questionDelete():
    q_id = request.args.get('q_id')
    querydb.questionDelete(q_id)
    return redirect(url_for('questions'))


@app.route('/questions')
@login_required
def questions():
    questions = querydb.getAllQuestions()
    #  count = querydb.paginate(page_num) --still working on pagination

    return render_template("questions.html", questions=questions)


@app.route('/add_questions')
@login_required
def add_questions():
    return render_template("add_question.html")


@app.route('/post_add_questions', methods=['GET', 'POST'])
def post_questions():
    # question = request.args.get('question')
    question = request.form.get('question')
    print(question);
    querydb.addQuestion(question, current_user.id)

    return redirect(url_for('questions'))


@app.route('/post_add_questionAnswers', methods=['GET', 'POST'])
def post_questionAnswers():
    # question = request.args.get('question')
    # question=request.form.get('question')
    # print(question);
    # querydb.addQuestion(question, current_user.id)

    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return 'This is protected page'


@app.route('/role')
@roles_required('admin')
def role():
    return 'you have permission'


@app.route('/parent')
def parent():
    return render_template('parent.html', children=Children)


@app.route('/admin')
@roles_required('admin')
def admin():
    users = querydb.getAllUsers()
    return render_template('admin.html', users=users)


class RoleChangeForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


class QuestionEdit(FlaskForm):
    question = StringField('question')
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
        # flash('Your changes have been saved.')
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
