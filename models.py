from peewee import *

# from flask_peewee_crud import generate_crud

__author__ = "Brandon Duke"

__version__ = ""
__email__ = "http://bduke.net"

"""
models:

Contains classes that are models for tables in the database
"""

""" the database connection string """
# brandon's db
db = MySQLDatabase("db9a6e80b2e34b41f3bd8da871003e804d",
                   host="9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com", port=3306, user="bgrwfoetjnrliplh",
                   passwd="GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw")
# jared lewis db
# db = MySQLDatabase("db38b32831bc8a4cf6acefa878003849f7", host="38b32831-bc8a-4cf6-acef-a878003849f7.sqlserver.sequelizer.com", port=3306, user="vnqimdibqlqhqgap", passwd="pdCJFgqiUjR68iGphryN5g6sdHEf3Voi7WQYPHvTpCFuyxdE3xkvYuQhgkF6Hjo8")


# Jason's
db = MySQLDatabase("db42576e98688b4ab28226a87601334c89",
                   host="42576e98-688b-4ab2-8226-a87601334c89.mysql.sequelizer.com", port=3306, user="mgqmsvhuvgtovyte",
                   passwd="Aqyg6kb6tqDJjNvvoJEDGqJv8xTytGnRm8L28MPrnQjztPMk3xupApKjNchFyKKU")


# Brandon's
# db = MySQLDatabase("db9a6e80b2e34b41f3bd8da871003e804d", host="9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com", port=3306, user="bgrwfoetjnrliplh", passwd="GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw")


class MySQLModel(Model):
    """A base model that will use our MySQL database"""

    class Meta:
        database = db


class user(MySQLModel):
    user_id = PrimaryKeyField()
    username = CharField()
    password = CharField()
    email = CharField()
    confirmed_at = DateTimeField()
    active = BooleanField()
    first_name = CharField()
    last_name = CharField()
    user_dob = DateTimeField()
    void_ind = CharField()

    class Meta:
        db_table = "user"


class parent(MySQLModel):
    parent_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")

    class Meta:
        db_table = "parent"


class child(MySQLModel):
    child_id = PrimaryKeyField()
    parent = ForeignKeyField(parent, to_field="parent_id")
    child_nm_fst = CharField()
    child_nm_lst = CharField()

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
    street_addr = CharField()
    city = CharField()
    providence = CharField()
    zip = CharField()

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
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    fee = DoubleField()
    paid = CharField()
    length = DoubleField()
    approved = CharField()

    class Meta:
        db_table = "consultation"


class consult_time(MySQLModel):
    cnslt_tm_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    time_st = DateTimeField()
    time_end = DateTimeField()
    approved = CharField()

    class Meta:
        db_table = "consult_time"


class notes(MySQLModel):
    note_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    note = CharField()
    user_id_crea = BigIntegerField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField()
    updt_dtm = DateTimeField()
    void_ind = CharField()

    class Meta:
        db_table = "notes"


class consultation_fee(MySQLModel):
    cnslt_fee_id = PrimaryKeyField()
    fee = DoubleField()
    void_ind = CharField

    class Meta:
        db_table = "consultation_fee"


class consultation_length(MySQLModel):
    cnslt_len_id = PrimaryKeyField()
    length = DoubleField()
    void_ind = CharField()

    class Meta:
        db_table = "consultation_length"


class questions(MySQLModel):
    q_id = PrimaryKeyField()
    question = CharField()
    user_id_crea = BigIntegerField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField()
    upd_dtm = DateTimeField()
    void_ind = CharField()

    class Meta:
        db_table = "questions"


class question_answers(MySQLModel):
    qa_id = PrimaryKeyField()
    child = ForeignKeyField(child, to_field="child_id")
    q = ForeignKeyField(questions, to_field="q_id")
    answer = CharField()

    class Meta:
        db_table = "question_answers"


class blog(MySQLModel):
    blog_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    text = CharField()
    crea_dtm = DateTimeField()
    user_id_upd = BigIntegerField()
    updt_dtm = DateTimeField()
    void_ind = CharField()

    class Meta:
        db_table = "blog"


class day_typ_cd(MySQLModel):
    day_typ_cd = PrimaryKeyField()
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


db.connect()
