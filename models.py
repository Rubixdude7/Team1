import datetime
from peewee import *

__author__ = "Brandon Duke"

__version__ = ""
__email__ = "http://bduke.net"

"""
models:

Contains classes that are models for tables in the database
"""

""" the database connection string """
allow_auto_seed = False

# DEV Jason's
#db = MySQLDatabase("db42576e98688b4ab28226a87601334c89", host="42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com", port=3306, user="mgqmsvhuvgtovyte", passwd="Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU")

# DEV2 sqlite (local)
#db = SqliteDatabase("local.db")
#allow_auto_seed = True

# Production Brandon's
db = MySQLDatabase("db9a6e80b2e34b41f3bd8da871003e804d", host="9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com", port=3306, user="bgrwfoetjnrliplh", passwd="GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw")

class MySQLModel(Model):
    """A base model that will use our MySQL database"""

    class Meta:
        database = db


class user(MySQLModel):
    user_id = PrimaryKeyField()
    username = CharField()
    password = CharField()
    email = CharField()
    confirmed_at = DateTimeField(null=True)
    active = BooleanField()
    first_name = CharField()
    last_name = CharField(null=True)

    class Meta:
        db_table = "user"


class child(MySQLModel):
    child_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")
    child_nm_fst = CharField()
    child_nm_lst = CharField(null=True)
    child_dob = DateTimeField()
    q_comp_dtm = DateTimeField(null=True)

    class Meta:
        db_table = "child"


class psychologist(MySQLModel):
    psyc_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")
    photo = CharField()
    qualifications = CharField()

    class Meta:
        db_table = "psychologist"


class contact(MySQLModel):
    contact_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")
    phone_no = CharField()
    address_1 = CharField()
    address_2 = CharField(null=True)
    city = CharField()
    providence = CharField(null=True)
    zip = CharField(null=True)

    class Meta:
        db_table = "contact"


class psychologist_child_xref(MySQLModel):
    pcx_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    child = ForeignKeyField(child, to_field="child_id")

    class Meta:
        db_table = "psychologist_child_xref"


class consultation(MySQLModel):
    cnslt_id = PrimaryKeyField()
    child = ForeignKeyField(child, to_field="child_id")
    fee = DoubleField()
    paid = CharField()
    length = DoubleField()
    finished = CharField()

    class Meta:
        db_table = "consultation"


class consult_time(MySQLModel):
    cnslt_tm_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    time_st = DateTimeField()
    time_end = DateTimeField()
    approved = CharField(null=True)

    class Meta:
        db_table = "consult_time"


class notes(MySQLModel):
    note_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    note = CharField()
    user_id_crea = BigIntegerField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField(null=True)
    updt_dtm = DateTimeField(null=True)
    void_ind = CharField()

    class Meta:
        db_table = "notes"


class consultation_fee(MySQLModel):
    cnslt_fee_id = PrimaryKeyField()
    fee = DoubleField()
    void_ind = CharField()

    class Meta:
        db_table = "consultation_fee"


class consultation_length(MySQLModel):
    cnslt_len_id = PrimaryKeyField()
    length = DoubleField()
    cnslt_fee = ForeignKeyField(consultation_fee, to_field="cnslt_fee_id")
    void_ind = CharField()

    class Meta:
        db_table = "consultation_length"


class questions(MySQLModel):
    q_id = PrimaryKeyField()
    question = CharField()
    user_id_crea = BigIntegerField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField(null=True)
    upd_dtm = DateTimeField(null=True)
    active = CharField()
    void_ind = CharField()

    class Meta:
        db_table = "questions"


class question_answers(MySQLModel):
    qa_id = PrimaryKeyField()
    child = ForeignKeyField(child, to_field="child_id")
    q = ForeignKeyField(questions, to_field="q_id")
    answer = CharField()
    qa_crea_dtm = DateTimeField()
    qa_upt_dtm = DateTimeField(null=True)
    void_ind = CharField()

    class Meta:
        db_table = "question_answers"


class blog(MySQLModel):
    blog_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    subject = CharField()
    text = CharField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField(null=True)
    updt_dtm = DateTimeField(null=True)
    void_ind = CharField()

    class Meta:
        db_table = "blog"


class day_typ_cd(MySQLModel):
    day_typ_cd = CharField(primary_key=True, max_length=2, db_column='day_tp_cd')
    day = CharField()

    class Meta:
        db_table = "day_typ_cd"


class calendar(MySQLModel):
    cal_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    time_st = TimeField()
    time_end = TimeField()
    day_typ_cd = ForeignKeyField(day_typ_cd, to_field="day_typ_cd", db_column="day_typ_cd")
    void_ind = CharField()

    class Meta:
        db_table = "calendar"


class review(MySQLModel):
    rev_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    review = CharField()
    stars = DoubleField()
    approved = CharField()
    void_ind = CharField()

    class Meta:
        db_table = "review"


class role(MySQLModel):
    role_id = PrimaryKeyField()
    role_nm = CharField()

    class Meta:
        db_table = "role"


class user_roles(MySQLModel):
    user_role_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")
    role = ForeignKeyField(role, to_field="role_id")

    class Meta:
        db_table = "user_roles"

class vacation(MySQLModel):
    vac_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    vac_st = DateTimeField()
    vac_end = DateTimeField()
    annual = BooleanField()
    
    class Meta:
        db_table = "vacation"

class slider(MySQLModel):
    slider_id = PrimaryKeyField()
    img = CharField()
    version = CharField()
    desc = CharField()
    alt = CharField()

    class Meta:
        db_table = "slider"


MODELS = [blog,
          calendar,
          child,
          consult_time,
          consultation,
          consultation_fee,
          consultation_length,
          contact,
          day_typ_cd,
          notes,
          psychologist,
          psychologist_child_xref,
          question_answers,
          questions,
          review,
          role,
          user,
          user_roles,
          vacation]

# This function does nothing if the db is already populated.
def create_tables_and_seed_if_necessary():
    if allow_auto_seed:
        db.create_tables(MODELS, safe=True)
        
        # Figure out which day_typ_cd entities we need
        dtc_needed = {
            'm': 'Senin',
            't': 'Selasa',
            'w': 'Rabu',
            'th': 'Kamis',
            'f': 'Jumat',
            's': 'Sabtu',
            'su': 'Minggu'
        }
        for dtc in day_typ_cd.select():
            if dtc.day_typ_cd in dtc_needed:
                del dtc_needed[dtc.day_typ_cd]
                
        # Make them
        for k, v in dtc_needed.items():
            day_typ_cd.create(day_typ_cd=k, day=v)
        
        # Same thing for roles
        roles_needed = [ 'admin', 'staff', 'psyc', 'user' ]
        for r in role.select():
            if r.role_nm in roles_needed:
                roles_needed.remove(r.role_nm)
        for name in roles_needed:
            role.create(role_nm=name)
        
        # If there are no users, make default users for each role
        if user.select().count() == 0:
            admin = user.create(username='PassionAdmin',
                                password='$2b$12$WGvSy4WqRbMogeSQBzQt8uMzLIfPm0swohryo469ShterBWJTk5SK',
                                email='passion.kon.psi@gmail.com',
                                confirmed_at=datetime.datetime.now(),
                                active=1,
                                first_name='Passion',
                                last_name='Admin')
            
            # Give them the admin role
            admin_role = role.select().where(role.role_nm == 'admin').get()
            user_roles.create(user=admin.user_id, role=admin_role.role_id)
            
            staff = user.create(username='PassionStaff',
                                password='$2b$12$WGvSy4WqRbMogeSQBzQt8uMzLIfPm0swohryo469ShterBWJTk5SK',
                                email='passion.kon.psi@gmail.com',
                                confirmed_at=datetime.datetime.now(),
                                active=1,
                                first_name='Passion',
                                last_name='Staff')
            
            # Give them the staff role
            staff_role = role.select().where(role.role_nm == 'staff').get()
            user_roles.create(user=staff.user_id, role=staff_role.role_id)
            
            psyc = user.create(username='PassionPsyc',
                               password='$2b$12$WGvSy4WqRbMogeSQBzQt8uMzLIfPm0swohryo469ShterBWJTk5SK',
                               email='passion.kon.psi@gmail.com',
                               confirmed_at=datetime.datetime.now(),
                               active=1,
                               first_name='Passion',
                               last_name='Psyc')
            
            # Give them the psyc role
            psyc_role = role.select().where(role.role_nm == 'psyc').get()
            user_roles.create(user=psyc.user_id, role=psyc_role.role_id)
            
            # Add a psychologist entity for them too
            psychologist.create(user=psyc.user_id, photo='', qualifications='A good psychologist.')
            
            u = user.create(username='PassionUser',
                            password='$2b$12$WGvSy4WqRbMogeSQBzQt8uMzLIfPm0swohryo469ShterBWJTk5SK',
                            email='passion.kon.psi@gmail.com',
                            confirmed_at=datetime.datetime.now(),
                            active=1,
                            first_name='Passion',
                            last_name='User')
            
            # Give them the user role
            u_role = role.select().where(role.role_nm == 'user').get()
            user_roles.create(user=u.user_id, role=u_role.role_id)
