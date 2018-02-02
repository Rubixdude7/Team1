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

from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
from data import Children  # part of the dummy data. This and the other dummy data stuff can be deleted later
import query
import models
from flask import flash, render_template, request, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')
Children = Children()  # part of the dummy data file

# Setup Flask-User

mail = Mail(app)


class MyRegisterForm(RegisterForm):
    first_name = StringField('First Name', validators=[DataRequired('First name is required')])
    last_name = StringField('Last Name', validators=[DataRequired('Last name is required')])


db_adapter = models.PeeweeAdapter(models.db, models.user)  # Register the User model
user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm)  # Initialize Flask-User

# set up query class as db
querydb = query.query()


# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    if models.db.is_closed():
        models.db.connect()


# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not models.db.is_closed():
        models.db.close()


# This hook ensures that a user is given a role when they sign up
# new user registered
@user_registered.connect_via(app)
def _after_register_hook(sender, user, **extra):
    role = models.role.get(models.role.role_nm == 'user')
    user_role = models.user_roles(user=user, role=role)
    user_role.save()

#           BRANDON         #


@app.route('/')
def index():
    return render_template("index.html")

#           END BRANDON         #


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
    print(question)
    print(current_user.user_id)
    querydb.addQuestion(question, current_user.user_id)

    return redirect(url_for('questions'))


@app.route('/post_add_questionAnswers', methods=['GET', 'POST'])
def post_questionAnswers():
    # question = request.args.get('question')
    # question=request.form.get('question')
    # print(question);
    # querydb.addQuestion(question, current_user.id)

    return redirect(url_for('index'))


@app.route('/parent')
@login_required
def parent():
    return render_template('parent.html', user=current_user.first_name + " " + current_user.last_name, children = querydb.getChildren(current_user.user_id))


@app.route('/parent/contact', methods=['POST'])
def contact():
    return render_template('contact.html')


# methods Brody added (may not work '-__- )
@app.route('/child/<int:child_id>')
@roles_required('user')
def child(child_id=None):
    if child_id is not None:
        child_info = querydb.findChild(child_id)
        if child_info is not None:
            return render_template('child.html', child_info=child_info)
    return render_template('parent.html')


@app.route('/childform')
@roles_required('user')
def childform():
    return render_template('childform.html')


@app.route('/childform', methods=['post'])
@roles_required('user')
def addChild():
    querydb.addChild(current_user.user_id, request.form.get('firstname'), request.form.get('lastname'))
    return parent()

# End Brody's


# Start Jason's code
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
        u_id = request.args.get('u_id')
        newRole = form.role.data
        if newRole == 'psyc':
            querydb.addPsychologistIfNotExist(u_id)
        querydb.updateUserRole(u_id, newRole)
        #flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    return render_template('edit.html', title='Edit Profile',
                           form=form)

@app.route('/delete')
def delete():
    user_id = request.args.get('u_id')
    querydb.softDeleteUser(user_id)
    return redirect(url_for('admin'))

# End Jason's code

@app.route('/psikolog/')
@app.route('/psikolog/<int:id>')
def psikolog(id=None):
    if id is not None:
        psyc_info = querydb.lookupPsychologist(id)
        if psyc_info is not None:
            return render_template('psikolog.html', psyc_info=psyc_info)

    # Either no id was given or no psychologist was found.
    # In both cases, show a list of psychologists.
    return render_template('list_psikolog.html', psychologist_links=querydb.psychologistLinks())


if __name__ == '__main__':
    app.run(debug=True)
