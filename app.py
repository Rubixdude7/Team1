from flask import Flask, render_template, request, redirect, url_for
import datetime
from flask_user import login_required, roles_required, UserManager, UserMixin, current_user, user_registered
from flask_user.forms import RegisterForm
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, Form, SelectField, SubmitField
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
from data import Children  # part of the dummy data. This and the other dummy data stuff can be deleted later
import models
import query

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')
Children = Children()  # part of the dummy data file

mail = Mail(app)


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
db_adapter = models.PeeweeAdapter(models.db, models.user)  # Register the User model
user_manager = UserManager(db_adapter, app, register_form=MyRegisterForm)  # Initialize Flask-User

# set up query class as db
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


# methods Brody added (may not work '-__- )
@app.route('/child')
def child():
    return render_template('child.html')


@app.route('/child', methods=['post'])
def addChild():

    # Ask how to get current user id for parent ID

    kid = models.child
    kid.child_nm_fst = request.form['firstname']
    kid.child_nm_lst = request.form['lastname']

    return render_template('parent.html', children=Children)

# End danger zone (Brody Land)

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
        user_id = request.args.get('u_id')
        newRole = form.role.data
        querydb.updateUserRole(user_id, newRole)
        # flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    return render_template('edit.html', title='Edit Profile',
                           form=form, current_user=current_user.id)

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

@app.route('/delete')
def delete():
    user_id = request.args.get('u_id')
    querydb.softDeleteUser(user_id)
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
