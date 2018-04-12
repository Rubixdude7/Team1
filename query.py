import calendar

from flask import Markup
import bleach
import models as db
import datetime
import pytz
import babel
from peewee import *
import cloudinary
import cloudinary.uploader
from _sha256 import sha256
from uuid import uuid4 #this is in place of js's guid
from jose import jws
from jose import jwt
import requests
import time
import json
import hashlib
from flask_mail import Message
from flask import render_template


class query(object):
    """A library of convenient database access methods. Ideally, all of the
    database interaction should be in this class.

    When this class is instantiated, cloudinary is automatically configured."""

    def __init__(self):
        cloudinary.config(
            cloud_name="hbcgsvmyc",
            api_key="483847116472347",
            api_secret="UYew22cMiFrua6LbuHUQey40ahE"
        )

    def deactivateQuestion(self, q_id):

        question = db.questions.get(db.questions.q_id == q_id)
        question.void_ind = 'y'
        question.save()

    def getQuestion(selfs, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        return question

    def reactivateQuestion(self, q_id):
        question = db.questions.get(db.questions.q_id == q_id)

        question.void_ind = 'n'
        question.save()

    def questionDelete(self, q_id):
        question = db.questions.get(db.questions.q_id == q_id)
        question.void_ind = 'd'

        question.save()
        question.save()

    def addQuestion(self, question2, user):

        q = db.questions(question=question2, user_id_crea=user, crea_dtm=datetime.datetime.now())
        q.save()

    def checkNewQuestions(self, user_id):
        questionsUpdated = []
        c = db.child.select().where(db.child.user == user_id)
        for child in c:
            print(child.child_id)
            x = child.q_comp_dtm
            if db.questions.select().where(db.questions.crea_dtm > x):
                questionsUpdated.append(child.child_id)

        print(questionsUpdated)
        return questionsUpdated

    def addQuestionAnswers(self, questionAnswer, user, q_id, childId):

        print("EG")
        print(questionAnswer)
        print(user)
        print(q_id)
        print(childId)
        # Begin Brody
        '''
            This should now prevent additional rows from being
            added unnecessarily, i.e., the answer didn't change for this kid, for this question
        '''
        alreadyExists = query.getAnswer(self, q_id, childId)
        if alreadyExists is None:
            print(alreadyExists)
            print("GIG")
            # Begin Jared
            current = db.child.get(db.child.child_id == childId)
            print(current)

            current.save()
            print("testing")
            print("ans", questionAnswer)
            print("q_id", q_id)
            print("child", childId)
            print("qacreatedtn", datetime.datetime.now())
            q = db.question_answers(answer=questionAnswer, qa_crea_dtm=datetime.datetime.now(), q=q_id,
                                    child=childId, void_ind='n')
            print("be", q)
            q.save()
            # End Jared
        elif alreadyExists == questionAnswer:
            print("Answer already exists and didn't change!")
        else:
            print("Updating answer")
            query.voidAnswer(self, q_id, childId)
            # Begin Jared
            current = db.child.get(db.child.child_id == childId)

            current.save()

            q = db.question_answers(answer=questionAnswer, user_id_crea=user, crea_dtm=datetime.datetime.now(),
                                    q=q_id,
                                    child=childId, void_ind='n')
            q.save()
            # End Jared
        # End Brody

    def paginate(self, num):
        num = db.questions.select()
        return num

    def checkComp(self, childId):
        current = db.child.get(db.child.child_id == childId)
        print('test3r')
        current.q_comp_dtm = datetime.datetime.now()
        current.save()

    def getAllQuestions(self):
        questions = db.questions.select().where(db.questions.void_ind != 'd')
        liste = list(questions.tuples())
        print(liste)
        if not liste:
            print("green")
        return questions
    def reviewsForChildren(self, child_id):
        current = db.consultation.select().where(db.consultation.child == child_id, db.consultation.finished == 'y')
        check = list(current.tuples())

        if check:
            x = current[-1].cnslt_id


            return x
    def checkConsultId(self, consult_id, user_id):
        print("CONSULT2", consult_id)
        try:
            current = db.consultation.get(db.consultation.cnslt_id == consult_id, db.consultation.finished == 'y')
            child = current.child_id
            current2 = db.child.get(db.child.child_id == child, db.child.user == user_id) #ensure this review can be accessed by user.
        except:
            return False

        if current:
            return True
        return False
    def checkIfReviewed(self, child_id):
        print("Ccre", child_id)
        try:
            x = db.consultation.get(db.consultation.child == child_id)
            id = x.cnslt_id
            print("id", id)
            z = db.review.get(db.review.cnslt == id)
            if z:
                if z.approved == 'd': #user can remake review
                    return False
                else:
                    return True
            else:
                return False
        except:
            return False

    def checkDupeChildName(self, first_name, last_name):
        try:
            x = db.child.get(db.child.child_nm_fst == first_name, db.child.child_nm_lst ==last_name)
            return True
        except:
            return False
    def checkExitingEditQuestion(self, q_id):
        try:
            x = db.questions.get(db.questions.q_id == q_id)
            return True
        except:
            return False

    def getAllUnapprovedReviews(self):
        tuples = db.review.select(db.review.rev_id, db.review.cnslt, db.review.review, db.review.stars, db.review.approved, db.review.crea_dtm, db.review.void_ind, db.consultation.fee, db.consultation.finished, db.child.user, db.user.username, db.user.email).join(db.consultation, JOIN_INNER, db.review.cnslt == db.consultation.cnslt_id).where(db.review.approved == 'n').join(db.child, JOIN_INNER, db.consultation.child == db.child.child_id).join(db.user, JOIN_INNER, db.child.user == db.user.user_id).tuples()


        return [{
            'rev_id': t[0],
            'cnslt': t[1],
            'review': Markup(t[2]),
            'stars': t[3],
            'approved': t[4],
            'time': t[5],
            'void_ind': t[6],
            'test': t[7],
            'finished': t[8],
            'user_id': t[9],
            'user': t[10],
            'email': t[11],

        } for t in tuples]


    def getAllApprovedReviews(self):
        tuples = db.review.select(db.review.rev_id, db.review.cnslt, db.review.review, db.review.stars,
                                  db.review.approved, db.review.crea_dtm, db.review.void_ind, db.consultation.fee,
                                  db.consultation.finished, db.child.user, db.user.username, db.user.email).join(
            db.consultation, JOIN_INNER, db.review.cnslt == db.consultation.cnslt_id).where(
            db.review.approved == 'y').join(db.child, JOIN_INNER, db.consultation.child == db.child.child_id).join(
            db.user, JOIN_INNER, db.child.user == db.user.user_id).tuples()

        return [{
            'rev_id': t[0],
            'cnslt': t[1],
            'review': Markup(t[2]),
            'stars': t[3],
            'approved': t[4],
            'time': t[5],
            'void_ind': t[6],
            'test': t[7],
            'finished': t[8],
            'user_id': t[9],
            'user': t[10],
            'email': t[11],

        } for t in tuples]
    def getReviewsOfPsyc(self, psyc_id):
        tuples = db.review.select(db.review.stars, db.review.review, db.consult_time.psyc, db.review.crea_dtm).join(db.consult_time, JOIN_INNER, db.review.cnslt == db.consult_time.cnslt).where(db.consult_time.psyc == psyc_id and db.review.approved =='y').tuples()
        totalReviews = len(tuples)
        totalStars = 0
        allReviews =[]
        for t in tuples:
            totalStars += int(t[0])
            allReviews.append(t[0])
        print("t" + str(totalReviews))
        print("t" + str(totalStars))

        return [ {
            'starAmount': t[0],
            'review': Markup(t[1]),
            'psyc_id': t[2],
            'crea_dtm': t[3],
        }

        for t in tuples], totalReviews, totalStars, allReviews
    def approveReview(self, r_id):
        print(r_id)
        review = db.review.get(db.review.rev_id == r_id)
        review.approved = 'y'
        review.save()
    def denyReview(self, r_id):
        review = db.review.get(db.review.rev_id == r_id)
        review.approved = 'd' #denied, no code to test denied. soft del

        review.save()


    def getAllQuestionsForUsers(self):
        questions = db.questions.select().where(db.questions.void_ind != 'd' and db.questions.void_ind == 'n')
        return questions

    def getAllQuestionAnswers(self, child_id):
        questionAnswers = db.question_answers.select().where(db.question_answers.child == child_id)
        return questionAnswers

    def editQuestion(self, a, newQuestion):
        current = db.questions.get(db.questions.q_id == a)
        current.question = newQuestion
        current.save()

    #  Brody's code

    def voidAnswer(self, q_id, child_id):
        q = db.question_answers.get(db.question_answers.q == q_id, db.question_answers.child == child_id, db.question_answers.void_ind == 'n')
        q.void_ind = 'y'
        q.save()

    def addChild(self, user_id, first, last, dob):
        c = db.child(user_id=user_id, child_nm_fst=first, child_nm_lst=last, child_dob=dob)
        c.save()

    def findChild(self, child_id):
        try:
            c = db.child.get(db.child.child_id == child_id)
            print(c.child_nm_fst)
            return c
        except:
            return None

    def getAnswer(self, question_id, child_id):
        try:
            a = db.question_answers.get(db.question_answers.q == question_id, db.question_answers.child == child_id, db.question_answers.void_ind == 'n')
            print("ABSWE", a.answer)
            return a.answer
        except:
            return None

    def getChildNameFromID(self, child_id):
        try:
            child = db.child.get(db.child.child_id == child_id)
            return child
        except:
            return None

    def getUnpaidConsultations(self):
        try:
            consultations = db.consultation.select().where(db.consultation.paid == 'n').order_by(db.consultation.cnslt_id.desc())
            return consultations
        except:
            return None

    def getPaidConsultations(self):
        try:
            consultations = db.consultation.select().where(db.consultation.paid == 'y').order_by(db.consultation.cnslt_id.desc())
            return consultations
        except:
            return None

    def markConsultApproved(self, consult_id):
        try:
            consultation = db.consultation.get(db.consultation.cnslt_id == consult_id)
            consultation.paid = 'y'
            consultation.save()

            user = db.user.select().where(db.user.user_id ==
                                          db.child.select(db.child.user).where(db.child.child_id ==
                                                                               db.consultation.select(db.consultation.child).where(db.consultation.cnslt_id == consult_id)))

            for u in user:
                user = u


            child = db.child.select(db.child.child_nm_fst, db.child.child_nm_lst).where(db.child.user == user.user_id).tuples()
            child = list(child)[0]
            child = child[0] + " " + child[1]


            cnslt_dtls = db.consultation.select(db.consultation.length, db.consultation.link, db.consult_time.time_st).where(db.consultation.cnslt_id == consult_id)\
                .join(db.consult_time, JOIN_INNER, db.consult_time.cnslt == db.consultation.cnslt_id).tuples()

            cnslt_dtls = list(cnslt_dtls)[0]

            length = cnslt_dtls[0]
            link = cnslt_dtls[1]
            date = cnslt_dtls[2].strftime("%B %d, %Y %I:%M %p")

            length = divmod(length, 1)
            x = int(length[1] * 60)
            y = int(length[0])
            length = str(y) + " hr(s) and " + str(x) + " mins"


            return user, child, length, link, date

        except Exception as e:
            print("approval error: " + str(e))
            print("Couldn't find consultation")
            return None

    def getConsultationTime(self, consult_id):
        try:
            time = db.consult_time.get(db.consult_time.cnslt == consult_id)
            return time
        except:
            print('Could not find that time')
    # End Brody's code

# Start Jason's code

    def getAllUsers(self, page_num, page_size, return_total=False):
        users = db.user.select().where(db.user.active).join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user).order_by(db.user_roles.role)

        if return_total:
            total = users.count()
            return total, users.paginate(page_num, page_size)
        else:
            return users.paginate(page_num, page_size)

    def getSearchedUsers(self, search, page_num, page_size, return_total=False):
        users = db.user.select().where(db.user.active & (db.user.username.contains(search) | db.user.email.contains(search))).join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user).order_by(db.user_roles.role)

        # users = db.user.select().where(db.user.active & db.user.email.contains(search)).paginate(page_num, num_of_pages)
        
        if return_total:
            total = users.count()
            return total, users.paginate(page_num, page_size)
        else:
            return users.paginate(page_num, page_size)

    def getUserCount(self):
        usercount = db.user.select().count()
        return usercount

    def getSearchedUserCount(self, search):
        usercount = db.user.select().where(db.user.active & db.user.email.contains(search)).count()
        return usercount


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
        user.active = False
        user.save()

    def role(self, id):
        role = db.role.select(db.role.role_nm).join(db.user_roles, JOIN_INNER, db.role.role_id ==
                                                    db.user_roles.select(db.user_roles.role).where(
                                                        db.user_roles.user == id)).tuples()
        role = list(role)[0][0]
        return role

    def getEmail(self, u_id):
        email = db.user.get(db.user.user_id == u_id)
        return email.email

    def getfName(self, u_id):
        name = db.user.get(db.user.user_id == u_id)
        return name.first_name

    def getlName(self, u_id):
        lName = db.user.get(db.user.user_id == u_id)
        return lName.last_name

    def getPhone(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.phone_no
        except DoesNotExist:
            return None

    def getAdd1(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.address_1
        except DoesNotExist:
            return None

    def getAdd2(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.address_2
        except DoesNotExist:
            return None

    def getCity(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.city
        except DoesNotExist:
            return None

    def getProvince(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.providence
        except DoesNotExist:
            return None

    def getZip(self, contact_id):
        try:
            c = db.contact.get(db.contact.contact_id == contact_id)
            return c.zip
        except DoesNotExist:
            return None

    def updateEmail(self, u_id, email):
        u = db.user.get(db.user.user_id == u_id)
        u.email = email
        u.save()

    def updateName(self, u_id, fname, lname):
        u = db.user.get(db.user.user_id == u_id)

        u.first_name = fname
        u.last_name = lname
        u.save()

    def updateLengthFee(self, length, fee):
        try:
            l = db.consultation_fee.get(db.consultation_fee.cnslt_fee_id == length)
        except:
            l = db.consultation_fee(fee=fee, void_ind="n")

        l.fee = fee
        l.save()

# End Jason's code

# Begin Charlie's code
    def getUserPsycId(self, u_id):
        '''Retrieves and returns the psychologist ID associated with a user.

        :param int u_id: The ID of the user.
        :return: The psychologist ID associated with the user, or -1 if not found.
        :rtype: int'''
        tuples = db.user.select(db.psychologist.psyc_id)\
                        .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                        .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                        .join(db.psychologist, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                        .where(db.user.active & (db.role.role_nm == 'psyc') & (db.user.user_id == u_id))\
                        .tuples()
        if len(tuples) == 0:
            return -1
        return tuples[0][0]

    def getBlogPostsBy(self, psyc_id):
        ''':deprecated:

        Retrieves blog posts by a particular psychologist.

        :param int psyc_id: the ID of the psychologist.
        :return: a list of :class:`models.blog` objects.
        :rtype: list'''
        blg = db.blog.select()\
                     .join(db.psychologist, JOIN_INNER, db.blog.psyc == db.psychologist.psyc_id)\
                     .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                     .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                     .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                     .where(db.user.active & (db.role.role_nm == 'psyc') & (db.psychologist.psyc_id == psyc_id))\
                     .order_by(db.blog.updt_dtm.desc())
        return blg

    def getAllBlogPosts(self, page_num, items_per_page):
        ''':deprecated:

        Retrieves paginated blog posts posts.

        :param int page_num: A page number.
        :param int items_per_page: The number of items you want per page.
        :return: A list of dicts.
        :rtype: list'''
        tuples = db.blog.select(db.blog.subject, db.blog.updt_dtm, db.blog.text, db.psychologist.psyc_id, db.user.first_name, db.user.last_name)\
                        .join(db.psychologist, JOIN_INNER, db.blog.psyc == db.psychologist.psyc_id)\
                        .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                        .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                        .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                        .where(db.user.active & (db.role.role_nm == 'psyc'))\
                        .order_by(db.blog.updt_dtm.desc())\
                        .paginate(page_num, items_per_page).tuples()

        return [{
            'title': t[0],
            'date_posted': t[1],
            'contents': Markup(t[2]),
            'psyc_id': t[3],
            'author': '{0} {1}'.format(t[4], t[5])
        } for t in tuples]

    def getAvatar(self, psyc_id):
        '''Returns the URL for a psychologist's avatar.

        :param int psyc_id: The ID of the psychologist.
        :return: The URL of the psychologist's avatar.
        :rtype: str'''
        psyc = db.psychologist.get(db.psychologist.psyc_id == psyc_id)
        if psyc.photo is None or psyc.photo == '':
            return '/static/noavatar.png'

        public_id, version = psyc.photo.split('#')

        return cloudinary.CloudinaryImage(public_id, version=version).build_url()

    def allowed_file(self, filename):
        '''Returns whether a filename's extension indicates that it is an image.

        :param str filename: A filename.
        :return: Whether the filename has an recognized image file extension
        :rtype: bool'''
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

    def updateAvatar(self, psyc_id, avatar_file):
        '''Updates the avatar of a psychologist.

        :param int psyc_id: The ID of the psychologist.
        :param file avatar_file: A filelike object found in **flask.request.files**.
        :return: True if successful, False if unsuccessful.
        :rtype: bool'''
        if not self.allowed_file(avatar_file.filename):
            return False

        response = cloudinary.uploader.upload(avatar_file)
        image_descriptor = response['public_id'] + '#' + str(response['version'])

        p = db.psychologist.get(db.psychologist.psyc_id == psyc_id)
        p.photo = image_descriptor
        p.save()

        return True

    def getPsycId(self, u_id):
        '''Retrieves and returns the psychologist ID associated with a user.

        :param int u_id: The ID of the user.
        :return: The psychologist ID associated with the user, or -1 if not found.
        :rtype: int'''
        results = db.user.select(db.psychologist.psyc_id)\
                        .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                        .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                        .join(db.psychologist, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                        .where(db.user.active & (db.user.user_id == u_id) & (db.role.role_nm == 'psyc')).tuples()
        if len(results) == 0:
            return -1
        psyc_id = results[0][0]
        return psyc_id

    def createBlogPost(self, u_id, psyc_id, subject, text):
        '''Creates a blog post in the database. For this to work, *u_id* must
        must be the ID of the user associated with the psychologist with ID
        *psyc_id*. The blog's subject is set to *subject* and its body text is
        set to *text*.

        :param int u_id: The ID of the user.
        :param int psyc_id: The psychologist ID associated with the user.
        :param str subject: The subject of the blog post.
        :param str text: The body text of the blog post.'''
        text = bleach.clean(text, tags=[u'a', u'abbr', u'acronym', u'b', u'blockquote', u'code', u'em', u'i', u'li', u'ol', u'strong', u'ul', u'p'])
        now = pytz.utc.localize(datetime.datetime.utcnow()).replace(tzinfo=None)
        blog_post = db.blog(psyc=psyc_id,
                            subject=subject,
                            text=text,
                            crea_dtm=now,
                            user_id_upd=u_id,
                            updt_dtm=now,
                            void_ind='n')
        blog_post.save()

    def createReview(self, u_id, consult_id, reviewAmount, text, approved): #basically charlies code
        '''Creates a review.

        :param int u_id: The ID of the user.
        :param int consult_id: the id of the consultation.
        :param str reviewAmount: The review amount of the blog post.
        :param str text: The body text of the review.'''
        text = bleach.clean(text,
                            tags=[u'a', u'abbr', u'acronym', u'b', u'blockquote', u'code', u'em', u'i', u'li', u'ol',
                                  u'strong', u'ul', u'p'])
        now = pytz.utc.localize(datetime.datetime.utcnow()).replace(tzinfo=None)
        check = db.review.get(db.review.cnslt == consult_id)

        review = db.review(cnslt=consult_id,
                            review=text,
                            stars=reviewAmount,
                            approved=approved,
                            void_ind='n',
                            crea_dtm = datetime.datetime.now())

        if not check: #check if d so user can resubmit review
            review.save()
        else:
            print("B1")
            if check.approved == 'd':
                print("T1")
                check.review=text
                check.stars=reviewAmount
                check.approved= 'n'
                check.save()
            else:
                print("UNABLE TO SAVE, CONSULT ID EXISTS WITH A REVIEW")
    
    def getBlogPost(self, blog_id):
        post = db.blog.select().where((db.blog.blog_id == blog_id) & (db.blog.void_ind == 'n')).get()
        return post

    def updateBlogPost(self, blog_id, u_id, psyc_id, subject, text):
        text = bleach.clean(text, tags=[u'a', u'abbr', u'acronym', u'b', u'blockquote', u'code', u'em', u'i', u'li', u'ol', u'strong', u'ul', u'p'])
        now = pytz.utc.localize(datetime.datetime.utcnow()).replace(tzinfo=None)
        
        blog_post = db.blog.select().where((db.blog.void_ind == 'n') & (db.blog.blog_id == blog_id) & (db.blog.psyc == psyc_id)).get()
        blog_post.subject = subject
        blog_post.text = text
        blog_post.user_id_upd = u_id
        blog_post.updt_dtm = now
        blog_post.save()
    
    def deleteBlogPost(self, blog_id, psyc_id):
        blog_post = db.blog.select().where((db.blog.void_ind == 'n') & (db.blog.blog_id == blog_id) & (db.blog.psyc == psyc_id)).get()
        blog_post.void_ind = 'y'
        blog_post.save()

    def updateQualifications(self, psyc_id, qualifications):
        psyc = db.psychologist.select().where(db.psychologist.psyc_id == psyc_id).get()
        psyc.qualifications = qualifications
        psyc.save()
        
    def apiBlog(self, psyc_id, page_num, page_size):
        # Limit api calls to fetch a max of 20 pages
        if page_size > 20:
            page_size = 20
        
        # Check whether the caller wants a specific psychologist
        psyc_cond = None
        if psyc_id == 'all':
            psyc_cond = db.psychologist.psyc_id.is_null(False)
        else:
            psyc_cond = db.psychologist.psyc_id == int(psyc_id)
        
        # Perform the query
        query = db.blog.select(db.blog.psyc.alias('psyc_id'), db.blog.blog_id, db.blog.crea_dtm, db.blog.subject, db.blog.text)\
                       .join(db.psychologist, JOIN_INNER, db.blog.psyc == db.psychologist.psyc_id)\
                       .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                       .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                       .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                       .where(db.user.active & (db.role.role_nm == 'psyc') & (db.blog.void_ind == 'n') & psyc_cond)\
                       .order_by(db.blog.crea_dtm.desc())
        
        wib = pytz.timezone('Asia/Jakarta')
        return {
            'total': query.count(),
            'posts': [{
                'psyc_id': post.psyc_id,
                'blog_id': post.blog_id,
                'date_posted': babel.dates.format_datetime(pytz.utc.localize(post.crea_dtm).astimezone(wib), format='EEEE, d MMMM yyyy hh:mm a (z)', tzinfo=wib, locale='id_ID'),
                'subject': post.subject,
                'text': post.text
            } for post in query.paginate(page_num, page_size)]
        }
    
    def apiAppointments(self, psyc_id, page_num, page_size):
        if page_size > 10:
            page_size = 10
        elif page_size < 1:
            page_size = 1
        
        # Perform the query
        query = db.consult_time.select(db.consult_time.time_st, db.consult_time.time_end, db.child.child_nm_fst.alias('first_name'), db.child.child_nm_lst.alias('last_name'))\
                               .join(db.psychologist, JOIN_INNER, db.consult_time.psyc == db.psychologist.psyc_id)\
                               .join(db.consultation, JOIN_INNER, db.consultation.cnslt_id == db.consult_time.cnslt)\
                               .join(db.child, JOIN_INNER, db.consultation.child == db.child.child_id)\
                               .where(db.psychologist.psyc_id == psyc_id)\
                               .order_by(db.consult_time.time_st.asc())\
                               .naive()
        
        wib = pytz.timezone('Asia/Jakarta')
        return {
            'total': query.count(),
            'appointments': [{
                'time_st': babel.dates.format_datetime(pytz.utc.localize(appt.time_st).astimezone(wib), format='EEEE, d MMMM yyyy hh:mm a (z)', tzinfo=wib, locale='id_ID'),
                'time_end': babel.dates.format_datetime(pytz.utc.localize(appt.time_end).astimezone(wib), format='EEEE, d MMMM yyyy hh:mm a (z)', tzinfo=wib, locale='id_ID'),
                'name': '{0} {1}'.format(appt.first_name, appt.last_name)
            } for appt in query.paginate(page_num, page_size)]
        }

    def addPsychologistIfNotExist(self, u_id):
        # Check if user already has psychologist row
        tuples = db.psychologist.select().where(db.psychologist.user == u_id).tuples()
        if len(tuples) >= 1:
            return

        # None exist, so go ahead and make one
        psyc = db.psychologist(user=u_id, photo='', qualifications='This psychologist has not listed their qualifications.')
        psyc.save()

    def lookupPsychologist(self, ident):
        tuples = db.psychologist.select(db.psychologist.psyc_id,
                                        db.psychologist.qualifications,
                                        db.user.first_name,
                                        db.user.last_name)\
                                .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                                .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                                .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                                .where(db.user.active & (db.role.role_nm == 'psyc') & (db.psychologist.psyc_id == ident))\
                                .tuples()
        if len(tuples) > 0:
            info_tuple = tuples[0]
            print(list(info_tuple))

            info = PsychologistLookupResult()
            info.psyc_id = info_tuple[0]
            info.qualifications = info_tuple[1]
            info.first_name = info_tuple[2]
            info.last_name = info_tuple[3]
            info.full_name = '{0} {1}'.format(info.first_name, info.last_name)
            return info

        print('nope')
        return None

    def getPsychologistNames(self):
        tuples = db.psychologist.select(db.psychologist.psyc_id, db.user.first_name, db.user.last_name)\
                               .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                               .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                               .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)\
                               .where(db.user.active & (db.role.role_nm == 'psyc'))\
                               .tuples()
        return [{ 'psyc_id': t[0], 'first_name': t[1], 'last_name': t[2] } for t in tuples]

    def getAvailability(self, avail_id, psyc_id):
        t = db.calendar.select(db.calendar.time_st, db.calendar.time_end, db.day_typ_cd.day_typ_cd)\
                       .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.calendar.psyc)\
                       .join(db.day_typ_cd, JOIN_INNER, db.calendar.day_typ_cd == db.day_typ_cd.day_typ_cd)\
                       .where((db.psychologist.psyc_id == psyc_id) & (db.calendar.cal_id == avail_id) & (db.calendar.void_ind == 'n'))\
                       .tuples()[0]
        return {
            'avail_id': avail_id,
            'time_st': t[0],
            'time_end': t[1],
            'weekday': t[2]
        }

    def getAvailabilities(self, psyc_id, page=0):
        q = db.calendar.select(db.calendar.cal_id, db.calendar.time_st, db.calendar.time_end, db.day_typ_cd.day_typ_cd)\
                       .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.calendar.psyc)\
                       .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                       .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                       .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)\
                       .join(db.day_typ_cd, JOIN_INNER, db.calendar.day_typ_cd == db.day_typ_cd.day_typ_cd)\
                       .where(db.user.active & (db.role.role_nm == 'psyc') & (db.psychologist.psyc_id == psyc_id) & (db.calendar.void_ind == 'n'))

        if page < 1:
            tuples = q.tuples()
        else:
            tuples = q.paginate(page, 20).tuples()

        return [{
            'avail_id': t[0],
            'st': { 'hour': t[1].hour, 'minute': t[1].minute },
            'end': { 'hour': t[2].hour, 'minute': t[2].minute },
            'weekday': ['m', 't', 'w', 'th', 'f', 's', 'su'].index(t[3])
        } for t in tuples]
        

    def getVacations(self, psyc_id='all', page=0):
        psyc_cond = None
        
        if psyc_id == 'all':
            psyc_cond = db.psychologist.psyc_id.is_null(False)
        else:
            psyc_cond = db.psychologist.psyc_id == psyc_id
        
        q = db.vacation.select()\
                       .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.vacation.psyc)\
                       .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                       .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                       .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)\
                       .where(db.user.active & (db.role.role_nm == 'psyc') & psyc_cond)

        if page >= 1:
            q = q.paginate(page, 20)
        
        return q

    def getVacation(self, psyc_id, vac_id):
        q = db.vacation.select()\
                       .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.vacation.psyc)\
                       .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                       .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                       .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)\
                       .where(db.user.active & (db.role.role_nm == 'psyc') & (db.psychologist.psyc_id == psyc_id) & (db.vacation.vac_id == vac_id))\
                       .get()
        return q
    
    def updateVacation(self, psyc_id, vac_id, vac_st, vac_end, annual):
        vac = getVacation(psyc_id, vac_id)
        vac.vac_st = vac_st.replace(tzinfo=None)
        vac.vac_end = vac_end.replace(tzinfo=None)
        vac.annual = annual
        vac.save()
        
    def addVacation(self, psyc_id, vac_st, vac_end, annual):
        # Turn into a naive datetime
        vac_st = vac_st.replace(tzinfo=None)
        vac_end = vac_end.replace(tzinfo=None)
        db.vacation.create(psyc=psyc_id, vac_st=vac_st, vac_end=vac_end, annual=annual)
        
    def deleteVacation(self, psyc_id, vac_id):
        db.vacation.delete().where((db.vacation.psyc == psyc_id) & (db.vacation.vac_id == vac_id)).execute()

    def getAllAvailabilities(self, psyc_id='all'):
        q = db.calendar.select(db.psychologist.psyc_id, db.calendar.cal_id, db.calendar.time_st, db.calendar.time_end, db.day_typ_cd.day_typ_cd)\
                       .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.calendar.psyc)\
                       .join(db.day_typ_cd, JOIN_INNER, db.calendar.day_typ_cd == db.day_typ_cd.day_typ_cd)\
                       .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                       .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                       .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)
        if psyc_id == 'all':
            q = q.where(db.user.active & (db.role.role_nm == 'psyc') & (db.calendar.void_ind == 'n'))
        else:
            q = q.where(db.user.active & (db.role.role_nm == 'psyc') & (db.calendar.void_ind == 'n') & (db.psychologist.psyc_id == psyc_id))
        tuples = q.tuples()
        return [{
            'psyc_id': t[0],
            'avail_id': t[1],
            'time_st': t[2],
            'time_end': t[3],
            'weekday': t[4]
        } for t in tuples]

    def getAvailabilitiesForDay(self, psyc_id, year, month, day):
        wkd_index = datetime.date(year, month, day).weekday()
        wkd_abbr = ['m', 't', 'w', 'th', 'f', 's', 'su'][wkd_index]

        tuples = db.calendar.select(db.calendar.time_st, db.calendar.time_end)\
                            .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.calendar.psyc)\
                            .join(db.day_typ_cd, JOIN_INNER, db.calendar.day_typ_cd == db.day_typ_cd.day_typ_cd)\
                            .where((db.psychologist.psyc_id == psyc_id) & (db.calendar.void_ind == 'n') & (db.day_typ_cd.day_typ_cd == wkd_abbr))\
                            .tuples()
        return [{
            'time_st': t[0],
            'time_end': t[1]
        } for t in tuples]

    def addAvailability(self, psyc_id, time_st, time_end, weekday):
        # Find the weekday in the db
        wkd = db.day_typ_cd.select(db.day_typ_cd.day_typ_cd).where(db.day_typ_cd.day_typ_cd == weekday).tuples()[0][0]
        avail = db.calendar(psyc=psyc_id, time_st=time_st, time_end=time_end, day_typ_cd=wkd, void_ind='n')
        avail.save()

    def deleteAvailability(self, avail_id, psyc_id):
        avail = db.calendar.select()\
                           .where((db.calendar.cal_id == avail_id) & (db.calendar.psyc == psyc_id))\
                           .get()
        avail.void_ind = 'y'
        avail.save()

    def updateAvailability(self, avail_id, psyc_id, time_st, time_end, weekday):
        # Find the weekday in the db
        wkd = db.day_typ_cd.select(db.day_typ_cd.day_typ_cd).where(db.day_typ_cd.day_typ_cd == weekday).tuples()[0][0]

        avail = db.calendar.select()\
                           .where((db.calendar.cal_id == avail_id) & (db.calendar.psyc == psyc_id) & (db.calendar.void_ind == 'n'))\
                           .get()
        avail.time_st = time_st
        avail.time_end = time_end
        avail.day_typ_cd = wkd
        avail.save()

    def getConsultations(self):
        tuples = db.consultation.select(db.consult_time.psyc, db.consultation.child, db.consult_time.time_st, db.consult_time.time_end)\
                                .join(db.consult_time, JOIN_INNER, db.consultation.cnslt_id == db.consult_time.cnslt)\
                                .join(db.psychologist, JOIN_INNER, db.consult_time.psyc == db.psychologist.psyc_id)\
                                .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                                .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                                .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                                .where((db.role.role_nm == 'psyc') & db.user.active)\
                                .tuples()

        result = [{
            'psyc_id': t[0],
            'child_id': t[1],
            'time_st': t[2],
            'time_end': t[3]
        } for t in tuples]
        return result

    def getAllSlotsThatCanBeBooked(self, psyc_id='all'):
        avail_list = self.getAllAvailabilities(psyc_id)

        slots = []

        wib = pytz.timezone('Asia/Jakarta')
                
        # Let's say the calendar is only valid up to 30 days ahead of today.
        today = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(wib).replace(tzinfo=None)
        for day_offset in range(31):
            day = today + datetime.timedelta(day_offset)

            # Find all availabilities that match this day, grouped by psychiatrist.
            wkd = day.weekday()
            for a in avail_list:
                # What weekday is this availability for?
                a_wkd = ['m', 't', 'w', 'th', 'f', 's', 'su'].index(a['weekday'])

                if wkd == a_wkd:
                    
                    st = wib.localize(datetime.datetime.combine(day.date(), a['time_st'])).astimezone(pytz.utc).replace(tzinfo=None)
                    end = wib.localize(datetime.datetime.combine(day.date(), a['time_end'])).astimezone(pytz.utc).replace(tzinfo=None)

                    # Add this availability to the result
                    slots.append({
                        'psyc_id': a['psyc_id'],
                        'st': st,
                        'end': end,
                        'valid': True # For pruning later
                    })

        # Now the tough part -- cut out all the appointments and vacations
        
        # First do appointments
        cnslt_list = self.getConsultations()
        for cnslt in cnslt_list:
            for slot in slots:
                if slot['valid'] and slot['psyc_id'] == cnslt['psyc_id']:
                    # Does this consultation cut into this slot?
                    if slot['st'] < cnslt['time_end'] and slot['end'] > cnslt['time_st']:
                        # Yes. The question is: in what WAY does it cut it?
                        if cnslt['time_st'] <= slot['st'] and cnslt['time_end'] >= slot['end']:
                            # It eats the whole thing?
                            slot['valid'] = False
                        elif cnslt['time_st'] <= slot['st'] and cnslt['time_end'] < slot['end']:
                            # It just bites off a piece on the left?
                            slot['st'] = cnslt['time_end']
                        elif cnslt['time_st'] > slot['st'] and cnslt['time_end'] >= slot['end']:
                            # It bites off a piece on the right?
                            slot['end'] = cnslt['time_st']
                        elif cnslt['time_st'] > slot['st'] and cnslt['time_end'] < slot['end']:
                            # It bites off the middle?
                            slots.append({'psyc_id': slot['psyc_id'], 'st': cnslt['time_end'], 'end': slot['end'], 'valid': True})
                            slot['end'] = cnslt['time_st']
        
        # Second do vacations
        vac_list = self.getVacations()
        for vac in vac_list:
            for slot in slots:
                if slot['valid'] and slot['psyc_id'] == vac.psyc_id:
                    # Does this consultation cut into this slot?
                    if slot['st'] < vac.vac_end and slot['end'] > vac.vac_st:
                        # Yes. The question is: in what WAY does it cut it?
                        if vac.vac_st <= slot['st'] and vac.vac_end >= slot['end']:
                            # It eats the whole thing?
                            slot['valid'] = False
                        elif vac.vac_st <= slot['st'] and vac.vac_end < slot['end']:
                            # It just bites off a piece on the left?
                            slot['st'] = vac.vac_end
                        elif vac.vac_st > slot['st'] and vac.vac_end >= slot['end']:
                            # It bites off a piece on the right?
                            slot['end'] = vac.vac_st
                        elif vac.vac_st > slot['st'] and vac.vac_end < slot['end']:
                            # It bites off the middle?
                            slots.append({'psyc_id': slot['psyc_id'], 'st': vac.vac_end, 'end': slot['end'], 'valid': True})
                            slot['end'] = vac.vac_st

        slots = list(filter(lambda s: s['valid'], slots))
        for s in slots:
            del s['valid']

        for slot in slots:
            st = pytz.utc.localize(slot['st']).astimezone(wib).replace(tzinfo=None)
            slot['st'] = {
                'year': st.year,
                'month': st.month,
                'day': st.day,
                'hour': st.hour,
                'minute': st.minute,
                'weekday': st.weekday()
            }
            
            end = pytz.utc.localize(slot['end']).astimezone(wib).replace(tzinfo=None)
            slot['end'] = {
                'year': end.year,
                'month': end.month,
                'day': end.day,
                'hour': end.hour,
                'minute': end.minute,
                'weekday': end.weekday()
            }
        
        return slots

    def getWeekDays(self):
        wkds = db.day_typ_cd.select()
        d = {}
        for wkd in wkds:
            d[wkd.day_typ_cd] = wkd.day
        return d

    def getWeekDayList(self):
        wkds = self.getWeekDays()
        return [wkds[d] for d in ['m', 't', 'w', 'th', 'f', 's', 'su']]

    def psychologistLinks(self):
        tuples = db.psychologist.select(db.psychologist.psyc_id,
                                        db.psychologist.photo,
                                        db.user.first_name,
                                        db.user.last_name)\
                                .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                                .join(db.user_roles, JOIN_INNER, db.user_roles.user == db.user.user_id)\
                                .join(db.role, JOIN_INNER, db.role.role_id == db.user_roles.role)\
                                .where(db.user.active & (db.role.role_nm == 'psyc'))\
                                .tuples()

        links = [PsychologistLink(t[0], '{2} {3}'.format(*t)) for t in tuples]
        return links

    # End Charlie's code

    #Beginnning of Gabe's code

    def getChildren(self, user_id):
        c = db.child.select().where(db.child.user == user_id)
        return c

    def getAge(self, child):
        born = datetime.datetime.strptime(child.child_dob.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age

    def contactID(self, user_id):
        try:
            c = db.contact.select().where(db.contact.user == user_id).get()
        except DoesNotExist:
            c = None
        return c

    def getContact(self, user_id):
        c = db.contact.select().where(db.contact.user == user_id)
        return c

    def updateContact(self, user_id, contact_id, phone_no, address_1, address_2, city, providence, zip):
        try:
            c = db.contact.select().where(db.contact.user == user_id).get()
            c.phone_no=phone_no
            c.address_1=address_1
            c.address_2=address_2
            c.city=city
            c.providence=providence
            c.zip=zip

        except DoesNotExist:
            c = db.contact(user=user_id, contact_id=contact_id, phone_no=phone_no, address_1=address_1,
                           address_2=address_2, city=city, providence=providence, zip=zip)

        c.save()

    def postConsult(self, child_id):
        query = db.consult_time.select().where(db.consultation.child == child_id).join(db.consultation, JOIN_INNER, db.consult_time.cnslt == db.consultation.cnslt_id).order_by(db.consult_time.time_end.desc())
        print('getting end')
        for ct in query:
            l = ct.time_end

            print('in end if')

            print(datetime.datetime.utcnow())
            print(l)

            if l >= datetime.datetime.utcnow():
                print('fale')
                return False
        
        print('true 2')
        return True


    def haveTime(self, child_id):
        start = db.consult_time.select().where(db.consultation.child == child_id).join(db.consultation, JOIN_INNER, db.consult_time.cnslt == db.consultation.cnslt_id).order_by(db.consult_time.time_end.desc()).get()
        wib = pytz.timezone('Asia/Jakarta')
        start = pytz.utc.localize(start.time_st).astimezone(wib)
        return babel.dates.format_datetime(start, format='EEEE, d MMMM yyyy hh:mm a (z)', tzinfo=wib, locale='id_ID')

    def generateToken(self, content):
        api_key = '65e63b43-a69b-7ea1-49f7-06046fa21aee'
        secret_key = '9369f8e0-fff8-e5a6-d2a4-363254aa5dbe'
        payload = {"jti": uuid4().hex,
                   "iss": api_key,
                   "iat": int(time.time()),
                   "sub": hashlib.sha256(content).hexdigest(),
                   "exp": int(time.time() + 10)}
        signed = jwt.encode(claims=payload, key=secret_key)
        return signed

    # def generateUrl(self):
    #     url = 'https://interviews.skype.com/api/interviews'
    #
    #     payload = {"code": "passion", "title": "passion consultation"}
    #
    #     data = json.dumps(payload).encode('ascii')
    #     token = query.generateToken(self, data)  # stores the token
    #
    #     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    #                'Content-Type': 'application/json',
    #                'Authorization': 'Bearer ' + token}
    #     req = requests.post(url=url, data=data, headers=headers)
    #     # print(req.text)
    #     body = req.__dict__
    #     requrl = json.loads(body.get('_content', {})).get('urls', {})[0].get('url')
    #     return requrl

    def updateConsult(self, consult_id, link):
        c = db.consultation.select(db.consultation.link).where(db.consultation.cnsl_id == consult_id).join(db.consultation, JOIN_INNER, db.consultation.child == db.child.child_id).tuples()
        c.link = db.consultation(link=link)
        c.save()
        return True
    #End of Gabe's code

    #Nolan's Code

    def getVerifiedChildren(self):
        children = []
        for consultation in db.consultation.select():
            if consultation.approved == "y" or consultation.paid == "n":
                children.append({
                    'firstName': consultation.child.child_nm_fst,
                    'lastName': consultation.child.child_nm_lst,
                    'childID':consultation.child.child_id,
                    'time':consultation.length
                })
        if len(children) == 0:
            pass
        return children

    def getUnverifiedChildren(self):
        children = []
        for consultation in db.consultation.select():
            if consultation.approved == "n":
                children.append({
                    'firstName': consultation.child.child_nm_fst,
                    'lastName': consultation.child.child_nm_lst,
                    'childID': consultation.child.child_id,
                    'time': consultation.length
                })
        if len(children) == 0:
            pass
        return children

    #End Nolan's Code

# Begin Brandon

    def get_len_fee(self):
        len_fee = db.consultation_length.select(db.consultation_length.cnslt_len_id, db.consultation_length.length,
                                                db.consultation_fee.fee).where(
            db.consultation_length.void_ind == 'n').join(db.consultation_fee, JOIN_INNER, (
                    db.consultation_length.cnslt_fee == db.consultation_fee.cnslt_fee_id) & (
                                                                     db.consultation_fee.void_ind == 'n')).tuples()
        len_fee = list(len_fee)

        return len_fee

    def schecule_cnslt(self, args):
        fee = db.consultation_fee.select(db.consultation_fee.fee).where(db.consultation_fee.void_ind == 'n').join(db.consultation_length, JOIN_INNER, (args['len'] == db.consultation_length.length) & (db.consultation_length.cnslt_fee == db.consultation_fee.cnslt_fee_id)).tuples()
        fee = list(fee)[0][0]
        time_st = list(map(int, args['st_dt'].split("-")))
        #time_st = time_st[0] + "-" + time_st[1] + "-" + time_st[2] + " " + time_st[3] + ":" + time_st[4]
        #Fix exception in firefox
        time_st = "%d-%02d-%02d %02d:%02d" % (time_st[0], time_st[1], time_st[2], time_st[3], time_st[4])
        
        wib = pytz.timezone('Asia/Jakarta')
        time_st = datetime.datetime.strptime(time_st, '%Y-%m-%d %H:%M')
        time_end = time_st + datetime.timedelta(hours=float(args['len']))

        # Make sure this time is actually available.
        slots = self.getAllSlotsThatCanBeBooked(int(args['psyc_id']))
        # Find a slot that fits the requested time.
        ok = False
        for s in slots:
            s_st = datetime.datetime(s['st']['year'], s['st']['month'], s['st']['day'], s['st']['hour'],
                                     s['st']['minute'])
            s_end = datetime.datetime(s['end']['year'], s['end']['month'], s['end']['day'], s['end']['hour'],
                                      s['end']['minute'])

            if time_st >= s_st and time_end <= s_end:
                ok = True
                break

        if ok:
            cnslt = db.consultation(child_id=args['child_id'], fee=fee, paid='n', length=args['len'], finished='n')
            cnslt.save()

            cnslt_tm = db.consult_time(cnslt_id=cnslt.cnslt_id, psyc_id=args['psyc_id'], time_st=wib.localize(time_st).astimezone(pytz.utc).replace(tzinfo=None), time_end=wib.localize(time_end).astimezone(pytz.utc).replace(tzinfo=None), approved='y')
            cnslt_tm.save()

            user = db.user.select().where(db.user.user_id ==
                                          db.child.select(db.child.user).where(db.child.child_id ==
                                                                               db.consultation.select(
                                                                                   db.consultation.child).where(
                                                                                   db.consultation.cnslt_id == cnslt.cnslt_id)))

            for u in user:
                user = u

            child = db.child.select(db.child.child_nm_fst, db.child.child_nm_lst).where(
                db.child.user == user.user_id).tuples()
            child = list(child)[0]
            child = child[0] + " " + child[1]

            length = args['len']
            date = wib.localize(time_st).astimezone(pytz.utc).replace(tzinfo=None).strftime("%B %d, %Y %I:%M %p")

            length = divmod(length, 1)
            x = int(length[1] * 60)
            y = int(length[0])
            length = str(y) + " hr(s) and " + str(x) + " mins"

            # insert into notification
            not_vars = [child]
            notification = db.notification(user=user.user_id, not_typ_cd="appt_req_u", not_vars=json.dumps(not_vars), not_st_dtm=datetime.datetime.now(), not_end_dtm=cnslt_tm.time_st)
            notification.save()
            not_vars = [fee, cnslt_tm.time_st.strftime("%B %d, %Y %I:%M %p"), child]
            notification = db.notification(user=user.user_id, not_typ_cd="appt_pment", not_vars=json.dumps(not_vars), not_st_dtm=datetime.datetime.now(), not_end_dtm=cnslt_tm.time_st)
            notification.save()

            return True, "Your appointment has been made, contact office staff for payment processing.",user, child, date, length, fee
        else:
            return False, "An invalid time range was specified."


    def getNotification(self, userID):

        # update old notifications that may no longer be needed because of time

        notif = db.notification.select().where(db.notification.not_end_dtm < datetime.datetime.now())

        for n in notif:
            n.dismissed = "y"
            n.save()

        notif = db.notification.select(db.notification.not_vars, db.notificaiton_type.not_typ, db.notification.not_id).where((db.notification.dismissed == "n") & (db.notification.user == userID) & (db.notification.not_st_dtm <= datetime.datetime.now()) & (db.notification.not_end_dtm >= datetime.datetime.now()))\
            .join(db.notificaiton_type, JOIN_INNER, db.notification.not_typ_cd == db.notificaiton_type.not_typ_cd).tuples()

        # get current notifications

        notifs = []
        for n in notif:
            notifs.append({"id": n[2], "notif": n[1] % tuple(json.loads(n[0]))})

        return notifs

    def dismissNotification(self, id):

        notif = db.notification.get(db.notification.not_id == id)

        notif.dismissed = "y"

        notif.save()



#End Brandon

class PsychologistLookupResult:
    def __init__(self):
        self.psyc_id = None
        self.qualifications = None
        self.first_name = None
        self.last_name = None
        self.full_name = None

class PsychologistLink:
    def __init__(self, id, full_name):
        self.id = id
        self.full_name = full_name
