import models as db
import datetime
from peewee import *
import cloudinary
import cloudinary.uploader


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
        cloudinary.config(
            cloud_name="hbcgsvmyc",
            api_key="483847116472347",
            api_secret="UYew22cMiFrua6LbuHUQey40ahE"
        )

    def deactivateQuestion(self, q_id):

        question = db.questions.get(db.questions.q_id == q_id)
        question
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

    # Brody's code

    def addChild(self, user_id, first, last):
        c = db.child(user_id=user_id, child_nm_fst=first, child_nm_lst=last)
        c.save()

    def findChild(self, child_id):
        c = db.child.get(db.child.child_id == child_id)
        return c
    # End Brody's code

# Start Jason's code

    def getAllUsers(self):
        users = db.user.select().where(db.user.active)
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
        user.active = False
        user.save()

    def bringHimBack(self):
        user = db.user.get(db.user.user_id == 3)
        user.void_ind = 'n'
        user.save()

    def role(self, id):
        role = db.role.select(db.role.role_nm).join(db.user_roles, JOIN_INNER, db.role.role_id ==
                                                    db.user_roles.select(db.user_roles.role).where(
                                                        db.user_roles.user == id)).tuples()
        role = list(role)[0][0]
        print(role)
        return role

# End Jason's code

# Begin Charlie's code
    def addPsychologistIfNotExist(self, u_id):
        # Check if user already has psychologist row
        tuples = db.psychologist.select().where(db.psychologist.user == u_id).tuples()
        if len(tuples) >= 1:
            return

        # None exist, so go ahead and make one
        psyc = db.psychologist(user=u_id, photo='', qualifications='This psychologist has not listed their qualifications.')
        psyc.save()

    def lookupPsychologist(self, ident):
        print(type(ident))
        print(ident)
        tuples = db.psychologist.select(db.psychologist.photo,
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
            info.photo = info_tuple[0]
            info.qualifications = info_tuple[1]
            info.first_name = info_tuple[2]
            info.last_name = info_tuple[3]
            info.full_name = '{0} {1}'.format(info.first_name, info.last_name)
            return info

        print('nope')
        return None

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

    def contactID(self, user_id):
        c = db.contact.select().where(db.contact.user_id == user_id).get()
        return c

    def getContact(self, user_id):
        c = db.contact.select().where(db.contact.user == user_id)
        return c

    def updateContact(self, user_id, contact_id, phone_no, address_1, address_2, city, providence, zip):
        c = db.contact(user_id, contact_id=contact_id, phone_no=phone_no, address_1=address_1, address_2=address_2, city=city, providence=providence, zip=zip)
        c.save()

    #End of Gabe's code

# Begin Brandon
    def get_slides(self):
        slider_a = []
        for slide in db.slider.select():
            slider_a.append({
                'id': slide.slider_id,
                'img': slide.img,
                'version': slide.version,
                'desc': slide.desc,
                'alt': slide.alt
            })
        return slider_a

    def get_slide(self, s_id):
        slide = db.slider.get(db.slider.slider_id == s_id)
        url = cloudinary.CloudinaryImage(slide.img, version=slide.version).image()
        slide = {
            'desc': slide.desc,
            'alt': slide.alt,
            'img': url
        }
        return slide

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

    def update_slide(self, s_id, img, desc, alt):
        slide = db.slider.get(db.slider.slider_id == s_id)
        if img and self.allowed_file(img.filename):
            upload = cloudinary.uploader.upload(img, public_id=slide.img)
            slide.version = upload['version']
        if desc is not None and desc != "":
            slide.desc = desc
        if alt is not None and alt != "":
            slide.alt = alt
        slide.save()

    def get_slider(self):
        slider_tag = []
        slider_desc = []
        for slide in db.slider.select().order_by(db.slider.slider_id.asc()):
            slider_tag.append(cloudinary.CloudinaryImage(slide.img, version=slide.version).image(alt=slide.alt))
            slider_desc.append(slide.desc)
        print(slider_tag)
        return slider_tag, slider_desc


#End Brandon

class PsychologistLookupResult:
    def __init__(self):
        self.photo = None
        self.qualifications = None
        self.first_name = None
        self.last_name = None
        self.full_name = None

class PsychologistLink:
    def __init__(self, id, full_name):
        self.id = id
        self.full_name = full_name
