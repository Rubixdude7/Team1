import models as db
import datetime
from peewee import *


class query(object):
    """
    query Class:

    A class to do different queries to the database
    """

    def __init__(self):
        """"
        Default Constructor
        There are no parameters, default is here as there has to be code in the constructor
        """

    def deactivateQuestion(self, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        question.void_ind = 'y'
        question.save()

    def getQuestion(selfs, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        return question;

    def reactivateQuestion(self, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        question.void_ind = 'n'
        question.save()

    def questionDelete(self, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        question.delete_instance()
        question.save()

    def addQuestion(self, question2, user):
        q = db.questions(question=question2, user_id_crea=user, crea_dtm=datetime.datetime.now())
        q.save()

    def paginate(self, num):
        count = db.questions.query.paginate(per_page=2, page=num, error_out=True)
        return count;

    def getAllQuestions(self):
        questions = db.questions.select()
        return questions

    def editQuestion(self, a, newQuestion):
        current = db.questions.get(db.questions.q_id == a)
        current.question = newQuestion
        current.save()

    def test(self):
        # used to get dat from app.py page methods
        data = db.user.select(db.user.first_name).where(db.user.user_id == 1).tuples()
        data = list(data)[0][0]
        return data

    def getAllUsers(self):
        users = db.user.select().where(db.user.void_ind == 'n')
        return users

    def getAllRoles(self):
        roles = db.role.select(db.role.role_nm)
        return roles

    def updateUserRole(self, a, r):
        user = db.user.select(db.user.user_id).where(db.user.user_id == a)
        userrole = db.user_roles.get(db.user_roles.user == user)
        roleid = db.role.select(db.role.role_id).where(db.role.role_nm == r)
        userrole.role = roleid
        userrole.save()

    def softDeleteUser(self, u_id):
        user = db.user.get(db.user.user_id == u_id)
        user.void_ind = 'y'
        user.save()

    def bringHimBack(self):
        user = db.user.get(db.user.user_id == 3)
        user.void_ind = 'n'
        user.save()

    def role(self, id):
        db.role.select(db.role.role_nm).join(db.user_roles, JOIN_FULL, db.role.role_id ==
                                             db.user_roles.select(db.user_roles.role.join(db.user, JOIN_FULL,
                                                                                          db.user_roles.user == db.user.user_id and db.user.user_id == id)))
