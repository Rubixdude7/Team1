import os
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
from werkzeug.utils import secure_filename
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, ValidationError
import query
import models
from flask import flash, render_template, request, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
# DEV Jason's database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mgqmsvhuvgtovyte:Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU@42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com/db42576e98688b4ab28226a87601334c89'
# Production Brandon's database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO make sure this is ok, this gets rid of the warning in the terminal
app.config['CSRF_ENABLED'] = True
app.config['USER_APP_NAME'] = 'Passion'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config.from_pyfile('config.cfg')

# Setup Flask-User

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
    last_name = db.Column(db.String(100), nullable=True, server_default='')

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))

    def is_active(self):
        return self.active

    def is_in_role(self, r):
        role_nm = db.session.query(Role.name).join(UserRoles, (Role.id == UserRoles.role_id) & (UserRoles.user_id == self.id)).all()
        rs = False
        for rn in role_nm:
            if r == rn[0]:
                rs = True
        return rs


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
    last_name = StringField('Last Name')


# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, UserClass=User)  # Register the User model
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
    role = Role.query.filter_by(name="user").first()
    user_role = UserRoles(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()

#           BRANDON         #


@app.route('/')
def index():
    slider = querydb.get_slider()
    return render_template("index.html", slides=slider[0], desc=slider[1])


@app.route('/slide-edit/<int:s_id>', methods=['GET', 'POST'])
@roles_required('admin')
def slide_edit(s_id):
    return render_template('slide_edit.html', slide=querydb.get_slide(s_id), s_id=s_id)


@app.route('/slide-update/<int:s_id>', methods=['GET', 'POST'])
@roles_required('admin')
def slide_update(s_id):
    querydb.update_slide(s_id, request.files.get('image', None), request.form.get('desc', None), request.form.get('alt', None))
    return redirect(url_for('admin'))


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
                           form=form, question=getQuestion)


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


@app.route('/questionsUserView')
@login_required
def questionsUserView():
    questions = querydb.getAllQuestions()
    #  count = querydb.paginate(page_num) --still working on pagination

    return render_template("questionsUserView.html", questions=questions)




@app.route('/add_questions')
@login_required
def add_questions():
    return render_template("add_question.html")


@app.route('/post_add_questions', methods=['GET', 'POST'])
def post_questions():
    # question = request.args.get('question')
    question = request.form.get('question')
    print(question)
    print(current_user.id)
    querydb.addQuestion(question, current_user.id)

    return redirect(url_for('questions'))


@app.route('/post_add_questionAnswers', methods=['GET', 'POST'])
def post_questionAnswers():
    # question = request.args.get('question')
    # question=request.form.get('question')
    # print(question);
    # querydb.addQuestion(question, current_user.id)

    return redirect(url_for('index'))

#Gabe
@app.route('/parent')
@login_required
@roles_required('user')
def parent():
    return render_template('parent.html', user=current_user.first_name + " " + current_user.last_name, children = querydb.getChildren(current_user.id), contact_info=querydb.contactID(current_user.id))


@app.route('/parent/contact')
@roles_required('user')
def contact():
    return render_template('contact.html', contact_info=querydb.contactID(current_user.id))


@app.route('/parent/contact', methods=['GET', 'POST'])
@roles_required('user')
def editContact():
    contact_id=querydb.contactID(current_user.id)
    querydb.updateContact(current_user.id, contact_id,request.form.get('phone_no'), request.form.get('address_1'),
                          request.form.get('address_2'), request.form.get('city'), request.form.get('providence'),
                          request.form.get('zip'))
    return parent()
#End Gabe


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
    querydb.addChild(current_user.id, request.form.get('firstname'), request.form.get('lastname'))
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

    return render_template('admin.html', users=users, roles=roles, usersandroles=usersandroles, slides=querydb.get_slides())


class RoleChangeForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


class QuestionEdit(FlaskForm):
    question = StringField('question')
    submit = SubmitField('Submit')


@app.route('/edit', methods=['GET', 'POST'])
@roles_required('admin')
def edit():
    u_id = request.args.get('u_id')
    if int(u_id) == int(current_user.id):
        return redirect(url_for('admin'))
    form = RoleChangeForm()
    roles = querydb.getAllRoles()
    current_role = querydb.role(u_id)
    rolenames = [current_role]
    for a in roles:
        if a.role_nm != current_role:
            rolenames.append(a.role_nm)
    form.role.choices = [(r, r) for r in rolenames]
    if form.validate_on_submit():
        #u_id = request.args.get('u_id')
        newRole = form.role.data
        if newRole == 'psyc':
            querydb.addPsychologistIfNotExist(u_id)
        querydb.updateUserRole(u_id, newRole)
        #flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    return render_template('edit.html', title='Edit Profile',form=form)

@app.route('/delete')
@roles_required('admin')
def delete():
    user_id = request.args.get('u_id')
    if int(user_id) == int(current_user.id):
        return redirect(url_for('admin'))
    querydb.softDeleteUser(user_id)
    return redirect(url_for('admin'))


@app.route('/editClient')
@roles_required('admin')
def editClient():
    2+4

# End Jason's code

@app.route('/psikolog/')
@app.route('/psikolog/<int:id>')
def psikolog(id=None):
    if id is not None:
        psyc_info = querydb.lookupPsychologist(id)
        if psyc_info is not None:
            # Got their info.
            # Now fetch their blog posts.
            tuples = querydb.getBlogPostsBy(id).tuples()
            blog_posts = [{
                'title': t[2][:15] + '...',
                'date_posted': t[3],
                'contents': t[2]
            } for t in tuples]

            can_edit = False
            if current_user.is_authenticated:
                logged_in_psyc = querydb.getUserPsycId(current_user.id)
                if logged_in_psyc == id:
                    can_edit = True

            return render_template('psikolog.html', psyc_info=psyc_info, blog_posts=blog_posts, can_edit=can_edit)

    # Either no id was given or no psychologist was found.
    # In both cases, show a list of psychologists.
    return render_template('list_psikolog.html', psychologist_links=querydb.psychologistLinks())

@app.route('/psikolog/write_blog_post', methods=['GET', 'POST'])
@roles_required('psyc')
def write_blog_post():
    if request.method == 'GET':
        return render_template('write_blog_post.html')
    elif request.method == 'POST':
        text = request.form['text']
        success, psyc_id = querydb.createBlogPost(current_user.id, text)
        if success:
            flash('Your blog post has been published.')
        else:
            flash('We could not publish your blog post.', 'error')
        return redirect(url_for('psikolog', id=psyc_id))

if __name__ == '__main__':
    app.run(debug=True)
"""
@app.route('/staff')
roles_required('staff')
def staff():

    return
"""