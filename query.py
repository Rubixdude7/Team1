import models as db
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

    def test(self):
        # used to get dat from app.py page methods
        data = db.user.select(db.user.first_name).where(db.user.user_id == 1).tuples()
        data = list(data)[0][0]
        return data

    def getAllUsers(self):
        users = db.user.select().where(db.user.void_ind == 'n') #TODO based on how flask-user works may need to change to active not void_ind, just needs tested
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
        role = db.role.select(db.role.role_nm).join(db.user_roles, JOIN_INNER, db.role.role_id ==
                                             db.user_roles.select(db.user_roles.role).where(db.user_roles.user == id)).tuples()
        role = list(role)[0][0]
        print(role)
        return role
