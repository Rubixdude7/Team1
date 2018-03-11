import os
from flask import Flask, render_template, request, redirect, url_for, Markup
import datetime
from flask_sqlalchemy import SQLAlchemy
from playhouse.flask_utils import object_list
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
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mgqmsvhuvgtovyte:Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU@42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com/db42576e98688b4ab28226a87601334c89'
# Production Brandon's databasee
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bgrwfoetjnrliplh:GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw@9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com/db9a6e80b2e34b41f3bd8da871003e804d'
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'), 410


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    #slider = querydb.get_slider()
    page_num = 1
    if 'page_num' in request.args:
        page_num = int(request.args['page_num'])
    return render_template("index.html", blog_posts=querydb.getAllBlogPosts(page_num, 10), page_num=page_num)
    #return render_template("index.html", slides=slider[0], desc=slider[1])


@app.route('/slide-edit/<int:s_id>', methods=['GET', 'POST'])
@roles_required('admin')
def slide_edit(s_id):
    return render_template('slide_edit.html', slide=querydb.get_slide(s_id), s_id=s_id)


@app.route('/slide-update/<int:s_id>', methods=['GET', 'POST'])
@roles_required('admin')
def slide_update(s_id):
    querydb.update_slide(s_id, request.files.get('image', None), request.form.get('desc', None), request.form.get('alt', None))
    return redirect(url_for('admin'))


@app.route('/consultation', methods=['GET', 'POST'])
@login_required
def consultation():
    cnslt = dict()
    cnslt['psyc'] = request.form.get('psyc', None)
    cnslt['len_fee'] = request.form.get('length', None)
    cnslt['date'] = request.form.get('date', None)
    cnslt['hour'] = request.form.get('hour', None)
    cnslt['min'] = request.form.get('min', None)
    cnslt['child_id'] = request.args.get('child_id')
    print(cnslt)
    querydb.get_psyc_cnslt(cnslt)

    params = querydb.get_consultation()
    return render_template("consultation.html", psycs=params[0], len_fee=params[1])


#           END BRANDON         #


@app.route('/editQuestion', methods=['GET', 'POST'])
def editQuestion():
    q_id = request.args.get('q_id')
    getQuestion = querydb.getQuestion(q_id)
    form = QuestionEdit(request.form)
    if form.validate_on_submit():
        newQuestion = form.question.data
        querydb.editQuestion(q_id, newQuestion)
        flash('Your changes have been saved.')
        return redirect(url_for('questions'))
    return render_template('editQuestion.html', title='Edit Question',
                           form=form, question=getQuestion)


@app.route('/questiondeactivate')
def questiondeactivate():
    q_id = request.args.get('q_id')
    querydb.deactivateQuestion(q_id)
    flash('Your blog post has been deactivated!')
    return redirect(url_for('questions'))


@app.route('/questionreactivate')
def questionreactivate():
    q_id = request.args.get('q_id')
    querydb.reactivateQuestion(q_id)
    flash('Your blog post has been reactivated!')
    return redirect(url_for('questions'))


@app.route('/questionDelete')
def questionDelete():
    q_id = request.args.get('q_id')
    querydb.questionDelete(q_id)
    flash('Question has been deleted!')
    return redirect(url_for('questions'))


@app.route('/questions/')
@login_required
def questions():
    questions = querydb.getAllQuestions()
    return object_list("questions.html", paginate_by=3, query=questions, context_variable='questions')




@app.route('/questionsUserView/', methods=['GET', 'POST'])
@login_required
def questionsUserView():
    totalQuestions = request.args.get('totalQuestions')
    child_id = request.args.get('child_id')
    child_name = request.args.get('child_name')
    c = querydb.findChild(child_id)

    # brody
    if c is None:
        return redirect(url_for('parent'))
    elif c.user.user_id != current_user.id:
        return redirect(url_for('parent'))
    page = request.args.get("page")
    if page is not None:
        page = int(page)
        if page >= 1:
            savePaginateAnswers()
    # end brody



    questions = querydb.getAllQuestionsForUsers()
    # Brody code
    answers = []
    for q in questions:
        answers.append(querydb.getAnswer(q.q_id, child_id))
    # end Brody code
    if totalQuestions is None:
        totalQuestions = len(questions) #for progress bar
        totalQuestions = int(totalQuestions)

    return object_list("questionsUserView.html", paginate_by=3, query=questions, context_variable='questions', child_id=child_id, child_name=child_name, answers=answers, totalQuestions=totalQuestions)


@app.route('/questionsUserView2/', methods=['GET', 'POST'])
@login_required
def questionsUserView2(): #post QuestionUserView
    #getargs
    totalQuestions = request.args.get('totalQuestions')
    totalQuestions = int(totalQuestions)
    page = request.args.get('page')
    totalPage = request.args.get('totalPage')
    child_id = request.args.get('child_id')
    child_name = request.args.get('child_name')

    #validation
    c = querydb.findChild(child_id)
    if c is None:
        return redirect(url_for('parent'))
    elif c.user.user_id != current_user.id:
        return redirect(url_for('parent'))

    paginate = 3 #how much each page should paginate by, change for differet number of questions per page(please change this value for other question views if you change)
    questions = querydb.getAllQuestionsForUsers()
    # Brody code
    answers = []
    for q in questions:
        answers.append(querydb.getAnswer(q.q_id, child_id))
    if page is not None:
        answers = answers[(paginate * (int(page)-1)): len(answers)]
    # End Brody code

    questionAnswerList = request.form.getlist('fname')

    questionIdList = request.form.getlist('qField')
    childId = request.form.get('cField')

    q_id = request.args.get('q_id')

    # Brody says: q = answer, q2 = questionId
    for (q, q2) in zip(questionAnswerList, questionIdList):
        # lack of this if was causing false "completed" question forms
        if q is not '':
            querydb.addQuestionAnswers(q, current_user.id, q2, childId)

    if page == totalPage:
        querydb.checkComp(child_id)
        return redirect(url_for('parent'))

    return object_list("questionsUserView.html", paginate_by=paginate, query=questions, context_variable='questions',
                       child_id=child_id, child_name=child_name, answers=answers, totalQuestions=totalQuestions)


#This path is currently not used, will remove if confirmed
@app.route('/questionsEditQuestions/')
@login_required
def questionsEditQuestions():
    # request args
    child_id = request.args.get('child_id')
    child_name = request.args.get('child_name')

    questions = querydb.checkNewQuestions(child_id)

    return object_list("questionsEditQuestions.html", paginate_by=3, query=questions, context_variable='questions', child_id=child_id, child_name=child_name)
#END



@app.route('/viewAnswers/')
@login_required
def viewAnswers():
    child_id = request.args.get('child_id')
    child_name = request.args.get('child_name')
    questions = querydb.getAllQuestionAnswers()
    #  count = querydb.paginate(page_num) --still working on pagination
    return object_list("questionsUserView.html", paginate_by=3, query=questions, context_variable='questions', child_id=child_id, child_name=child_name)






@app.route('/parent_seeanswers')
@login_required
def parent_seeanswers():
    child_id = request.args.get('child_id')
    c = querydb.findChild(child_id)
    if c is None:
        return redirect(url_for('parent'))
    elif current_user.id is not c.user.user_id:
        return redirect(url_for('parent'))
    questions = querydb.getAllQuestionsForUsers()
    # Brody code
    answers = []
    for q in questions:
        print("Q_ID: ", q.q_id)
        answers.append(querydb.getAnswer(q.q_id, child_id))
    # end Brody code
    return render_template("parent_seeanswers.html", child_id=child_id, answers=answers, questions=questions)


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


#Gabe
@app.route('/parent')
@login_required
@roles_required('user')
def parent():

    updatedQuestions = querydb.checkNewQuestions(current_user.id)
    return render_template('parent.html', user=current_user.first_name + " " + current_user.last_name,
                           children = querydb.getChildren(current_user.id),
                           contact_info=querydb.contactID(current_user.id), querydb=querydb, updatedQuestions = updatedQuestions)


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


# Start Brody's code

# this may be code thats not used anymore?
@app.route('/child/<int:child_id>')
def child(child_id=None):

    r = querydb.role(current_user.id)
    if r == 'user' or r == 'admin' or r == 'staff' or r == 'psyc':
        child_info = querydb.findChild(child_id)
        if child_info is None:
            return redirect(url_for('index'))
        born = datetime.datetime.strptime(child_info.child_dob.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if age < 0:
            return redirect(url_for('index'))
        else:
            updatedQuestions = querydb.checkNewQuestions(child_id)
            print("updated", updatedQuestions)
            return render_template('child.html', child_info=child_info, child_age=age, updatedQuestions=updatedQuestions)
    else:
        return redirect(url_for('index'))
#end code that is not used anymore.



@app.route('/childform')
@roles_required('user')
def childform():
    return render_template('childform.html')


@app.route('/childform', methods=['post'])
@roles_required('user')
def addChild():
    born = datetime.datetime.strptime(request.form.get('dateofbirth'), "%Y-%m-%d")
    today = datetime.date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if age < 0:
        return parent()
    querydb.addChild(current_user.id, request.form.get('firstname'), request.form.get('lastname'), request.form.get('dateofbirth'))
    return parent()


@app.route('/post_add_questionAnswers', methods=['GET', 'POST'])
def savePaginateAnswers():

    questionAnswerList = request.form.getlist('fname')
    questionIdList = request.form.getlist('qField')
    childId = request.form.get('cField')
    q_id = request.args.get('q_id')


    # Brody says: q = answer, q2 = questionId
    for (q,q2) in zip (questionAnswerList, questionIdList):
      # lack of this if was causing false "completed" question forms
      if q is not '':
          querydb.addQuestionAnswers(q, current_user.id, q2, childId)


# End Brody

@app.route('/post_edit_questionAnswers', methods=['GET', 'POST'])
def post_editQuestions():
    questionAnswerList = request.form.getlist('fname')
    questionIdList = request.form.getlist('qField')
    childId = request.form.get('cField')
    q_id = request.args.get('q_id')

    for (q, q2) in zip(questionAnswerList, questionIdList):
        print(current_user.id)
        print(questionAnswerList)
        querydb.addQuestionAnswers(q, current_user.id, q2, childId)

    # question = request.args.get('question')
    # question=request.form.get('question')
    # print(question);
    # querydb.addQuestion(question, current_user.id)

    return redirect(url_for('parent'))

# Start Jason's code

# Forms
class RoleChangeForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


class EditClientForm(FlaskForm):
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    firstName = StringField('firstName')
    lastName = StringField('lastName')


class QuestionEdit(FlaskForm):
    question = StringField('question')
    submit = SubmitField('Submit')


class ClientEditForm(FlaskForm):
    email = StringField('Email')
    fName = StringField('First Name')
    lName = StringField('Last Name')
    phone = StringField('Phone Number')
    address_1 = StringField('Address 1')
    address_2 = StringField('Address 2')
    city = StringField('City')
    province = StringField('Province')
    zip = StringField('Zip Code')
    role = SelectField('Role', coerce=str, validators=[DataRequired()], option_widget='Select')
    submit = SubmitField('Submit')


class SearchBar(FlaskForm):
    search = StringField('Search', default='Search')
    submit = SubmitField('Submit')


# Routes
@app.route('/admin', methods=['GET', 'POST'])
@roles_required('admin')
def admin():
    page_num = 1
    if 'page_num' in request.args:
        page_num = int(request.args['page_num'])
    form = SearchBar()
    if form.validate_on_submit():
        users = querydb.getSearchedUsers(form.search.data, page_num, 5)
        num_of_pages = round(querydb.getSearchedUserCount(form.search.data) / 5)
    else:
        users = querydb.getAllUsers(page_num, 5)
        num_of_pages = round(querydb.getUserCount() / 5)
    roles = list()
    usersandroles = dict()
    for u in users:
        r = querydb.role(u.user_id)
        roles.append(r)
        if r == 'admin':
            usersandroles[u.email] = 'Admin'
        if r == 'user':
            usersandroles[u.email] = 'User'
        if r == 'psyc':
            usersandroles[u.email] = 'Psychologist'
        if r == 'staff':
            usersandroles[u.email] = 'Office Staff'
    return render_template('admin/admin.html', users=users, roles=roles, usersandroles=usersandroles, form=form
                           , page_num=page_num, num_of_pages=num_of_pages)


@app.route('/edit', methods=['GET', 'POST'])
@roles_required('admin')
def edit():
    isUserOrPsyc = False
    u_id = request.args.get('u_id')
    if int(u_id) == int(current_user.id):
        return redirect(url_for('admin'))
    current_role = querydb.role(u_id)
    c_id = querydb.contactID(u_id)
    if current_role == 'user' or current_role == 'psyc':
        form = ClientEditForm()
        form.email.default = querydb.getEmail(u_id)
        form.fName.default = querydb.getfName(u_id)
        form.lName.default = querydb.getlName(u_id)
        form.phone.default = querydb.getPhone(c_id)
        form.address_1.default = querydb.getAdd1(c_id)
        form.address_2.default = querydb.getAdd2(c_id)
        form.city.default = querydb.getCity(c_id)
        form.province.default = querydb.getProvince(c_id)
        form.zip.default = querydb.getZip(c_id)
        isUserOrPsyc = True
    else:
        form = RoleChangeForm()
    roles = querydb.getAllRoles()
    current_role = querydb.role(u_id)
    rolenames = [current_role]
    roleplusbigbois = dict()
    for a in roles:
        if a.role_nm != current_role:
            rolenames.append(a.role_nm)
    for name in rolenames:
        if name == 'user':
            roleplusbigbois['user'] = 'User'
        elif name == 'psyc':
            roleplusbigbois['psyc'] = 'Psychologist'
        elif name == 'admin':
            roleplusbigbois['Admin'] = 'Admin'
        elif name == 'staff':
            roleplusbigbois['staff'] = 'Office Staff'
    form.role.choices = [(r, roleplusbigbois[r]) for r in roleplusbigbois]
    if form.validate_on_submit():
        newRole = form.role.data
        if newRole == 'psyc':
            querydb.addPsychologistIfNotExist(u_id)
        querydb.updateUserRole(u_id, newRole)
        if isUserOrPsyc:
            querydb.updateEmail(u_id, form.email.data)
            querydb.updateName(u_id,form.fName.data,form.lName.data)
            querydb.updateContact(u_id, c_id, form.phone.data, form.address_1.data, form.address_2.data,
                                  form.city.data, form.province.data, form.zip.data)
        flash('Your changes have been saved.')
        return redirect(url_for('admin'))
    else:
        form.process()
    return render_template('admin/edit.html', title='Edit Profile', form=form, isUserOrPsyc=isUserOrPsyc)


@app.route('/delete')
@roles_required('admin')
def delete():
    user_id = request.args.get('u_id')
    if int(user_id) == int(current_user.id):
        return redirect(url_for('admin'))
    querydb.softDeleteUser(user_id)
    return redirect(url_for('admin'))


# End Jason's code

# Begin Charlie's code

@app.route('/my_psikolog_page')
@roles_required('psyc')
def my_psikolog_page():
    psyc_id = querydb.getPsycId(current_user.id)
    return redirect(url_for('psikolog', id=psyc_id))

@app.route('/psikolog/')
@app.route('/psikolog/<int:id>')
def psikolog(id=None):
    if id is not None:
        psyc_info = querydb.lookupPsychologist(id)
        if psyc_info is not None:
            # Got their info.
            # Now fetch their blog posts.
            blg = querydb.getBlogPostsBy(id)
            blog_posts = [{
                'title': post.subject,
                'date_posted': post.updt_dtm,
                'contents': Markup(post.text)
            } for post in blg]

            can_edit = False
            if current_user.is_authenticated:
                logged_in_psyc = querydb.getUserPsycId(current_user.id)
                if logged_in_psyc == id:
                    can_edit = True

            # Fetch the psychologist's avatar
            avatar_url = querydb.getAvatar(id)
            
            availabilities = querydb.getAvailabilities(id)

            return render_template('psikolog.html', psyc_info=psyc_info, blog_posts=blog_posts, can_edit=can_edit, avatar_url=avatar_url, availabilities=availabilities)

    # Either no id was given or no psychologist was found.
    # In both cases, show a list of psychologists.
    return render_template('list_psikolog.html', psychologist_links=querydb.psychologistLinks())

@app.route('/psikolog/<int:psyc_id>/<int:year>/<int:month>/<int:day>')
def view_day(psyc_id, year, month, day):
    psyc = querydb.lookupPsychologist(psyc_id)
    avails = querydb.getAvailabilitiesForDay(psyc_id, year, month, day)
    return render_template('view_day.html', psyc=psyc, year=year, month=month, day=day, avails=avails)

@app.route('/psikolog/write_blog_post', methods=['GET', 'POST'])
@roles_required('psyc')
def write_blog_post():
    if request.method == 'GET':
        return render_template('write_blog_post.html')
    elif request.method == 'POST':
        subject = request.form['subject']
        text = request.form['text']
        psyc_id = querydb.getPsycId(current_user.id)
        querydb.createBlogPost(current_user.id, psyc_id, subject, text)
        flash('Your blog post has been published.')
        return redirect(url_for('psikolog', id=psyc_id))

@app.route('/psikolog/change_avatar', methods=['GET', 'POST'])
@roles_required('psyc')
def change_avatar():
    if request.method == 'GET':
        return render_template('change_avatar.html', psyc_id=querydb.getPsycId(current_user.id))
    elif request.method == 'POST':
        psyc_id = querydb.getPsycId(current_user.id)
        querydb.updateAvatar(psyc_id, request.files['avatar'])
        flash('Avatar updated.')
        return redirect(url_for('psikolog', id=psyc_id))

@app.route('/psikolog/edit_qualifications', methods=['GET', 'POST'])
@roles_required('psyc')
def edit_qualifications():
    if request.method == 'GET':
        return render_template('edit_qualifications.html', psyc_id=querydb.getPsycId(current_user.id))
    elif request.method == 'POST':
        psyc_id = querydb.getPsycId(current_user.id)
        querydb.updateQualifications(psyc_id, request.form['qualifications'])
        flash('Qualifications updated.')
        return redirect(url_for('psikolog', id=psyc_id))
        
@app.route('/psikolog/edit_availability_list')
@roles_required('psyc')
def edit_availability_list():
    psyc_id = querydb.getPsycId(current_user.id)
    availabilities = querydb.getAvailabilities(psyc_id)
    weekdays = querydb.getWeekDays()
    return render_template('edit_availability_list.html', psyc_id=psyc_id, availabilities=availabilities, weekdays=weekdays)

@app.route('/psikolog/delete_availability/<int:avail_id>')
@roles_required('psyc')
def delete_availability(avail_id):
    psyc_id = querydb.getPsycId(current_user.id)
    querydb.deleteAvailability(avail_id, psyc_id)
    flash('Availability time has been deleted.')
    return redirect(url_for('edit_availability_list'))

@app.route('/psikolog/add_availability', methods=['GET', 'POST'])
@roles_required('psyc')
def add_availability():
    if request.method == 'GET':
        weekdays = querydb.getWeekDays()
        return render_template('add_availability.html', weekdays=weekdays)
    elif request.method == 'POST':
        psyc_id = querydb.getPsycId(current_user.id)
        time_st = request.form['time_st']
        time_end = request.form['time_end']
        weekday = request.form['weekday']
        
        querydb.addAvailability(psyc_id, time_st, time_end, weekday)
        
        flash('Your new availability time has been created.')
        
        return redirect(url_for('edit_availability_list'))
        
@app.route('/psikolog/edit_availability/<int:avail_id>', methods=['GET', 'POST'])
@roles_required('psyc')
def edit_availability(avail_id):
    psyc_id = querydb.getPsycId(current_user.id)
    if request.method == 'GET':
        avail = querydb.getAvailability(avail_id, psyc_id)
        weekdays = querydb.getWeekDays()
        return render_template('edit_availability.html', avail=avail, avail_id=avail_id, weekdays=weekdays)
    elif request.method == 'POST':
        time_st = request.form['time_st']
        time_end = request.form['time_end']
        weekday = request.form['weekday']

        if time_st < time_end:
            querydb.updateAvailability(avail_id, psyc_id, time_st, time_end, weekday)
            flash('Availability time has been updated.')
        else:
            flash('Failed to add availability time.  "Time Start" must be earlier than "Time End".', category='error')
        
        return redirect(url_for('edit_availability_list'))

# End Charlie's code

#Nolan's Code

@app.route('/staff')
@roles_required('staff')
def staff():
    return render_template('staff.html', children = querydb.getVerifiedChildren())

#End Nolan's Code


if __name__ == '__main__':
    app.run(debug=True)
