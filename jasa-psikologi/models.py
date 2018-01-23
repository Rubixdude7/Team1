from peewee import *

__author__ = "Brandon Duke"

__version__ = ""
__email__ = "http://bduke.net"

"""
models:

Contains classes that are models for tables in the database
"""


""" the database connection string """
db = MySQLDatabase("spice_rack", host="9a6e80b2-e34b-41f3-bd8d-a871003e804d.mysql.sequelizer.com", port=3306, user="bgrwfoetjnrliplh", passwd="GRShWRVNEtekUUFPP647rgrHZSjGghQFxWjv8uMuAax4C8aL8bUxQC8AyipdFoGw")


class MySQLModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db


class user(MySQLModel):
    user_id = PrimaryKeyField()
    username = CharField()
    user_nm_fst = CharField()
    user_nm_lst = CharField()
    user_email = CharField()
    user_pass = CharField()
    user_dob = DateField()
    verified = BooleanField()
    void_ind = CharField

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

    class Meta:
        db_table = "psychologist"


class psychologist_child_xref(MySQLModel):
    pcx_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    child = ForeignKeyField(child, to_field="child_id")

    class Meta:
        db_table = "psychologist_child_xref"


class consultation(MySQLModel):
    cnslt = PrimaryKeyField()
    child = ForeignKeyField(child, to_field="child_id")
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    fee = DoubleField()
    paid = DoubleField()
    length = DoubleField()
    approved = BooleanField()

    class Meta:
        db_table = "consultation"


class consult_time(MySQLModel):
    cnslt_tm_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    time_st = DateTimeField()
    time_end = DateField()
    approved = BooleanField()

    class Meta:
        db_table = "consult_time"


class notes(MySQLModel):
    note_id = PrimaryKeyField()
    cnslt = ForeignKeyField(consultation, to_field="cnslt_id")
    note = CharField()
    user_id_crea = BigIntegerField()
    crea_dtm = TimestampField()
    user_id_updt = BigIntegerField()
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


class questinoare(MySQLModel):
    q_id = PrimaryKeyField()
    void_ind = CharField()

    class Meta:
        db_table = "questionare"


class questionare_answers(MySQLModel):
    qa_id = PrimaryKeyField()
    child = ForeignKeyField(child, to_field="child_id")
    void_ind = CharField()

    class Meta:
        db_table = "questionare_answers"


class blog(MySQLModel):
    blog_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")
    text = CharField()
    crea_dtm = TimestampField()
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


class reviews(MySQLModel):
    rev_id = PrimaryKeyField()
    psyc = ForeignKeyField(psychologist, to_field="psyc_id")

    class Meta:
        db_table = "reviews"


class role(MySQLModel):
    role_id = PrimaryKeyField()
    role_nm = CharField()

    class Meta:
        db_table = "role"


class user_role_xref(MySQLModel):
    urx_id = PrimaryKeyField()
    user = ForeignKeyField(user, to_field="user_id")
    role = ForeignKeyField(role, to_field="role_id")

    class Meta:
        db_table = "user_role_xref"


db.connect()