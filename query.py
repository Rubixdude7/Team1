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

    def addQuestionAnswers(self, questionAnswer, user, q_id, childId):
        q = db.question_answers(answer=questionAnswer, user_id_crea=user, crea_dtm=datetime.datetime.now(), q=q_id, child=childId)
        q.save()

    def paginate(self, num):
        num = db.questions.select()
       # count = db.questions.paginate(per_page=2, page=num, error_out=True)
        return num;

    def getAllQuestions(self):
        questions = db.questions.select()
        return questions
    def getAllQuestionAnswers(self):
        questionsAnswers = db.question_answers.select()
        return questionsAnswers

    def editQuestion(self, a, newQuestion):
        current = db.questions.get(db.questions.q_id == a)
        current.question = newQuestion
        current.save()

    # Brody's code

    def addChild(self, user_id, first, last, dob):
        c = db.child(user_id=user_id, child_nm_fst=first, child_nm_lst=last, child_dob=dob)
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

    def role(self, id):
        role = db.role.select(db.role.role_nm).join(db.user_roles, JOIN_INNER, db.role.role_id ==
                                                    db.user_roles.select(db.user_roles.role).where(
                                                        db.user_roles.user == id)).tuples()
        role = list(role)[0][0]
        return role

# End Jason's code

# Begin Charlie's code
    def getUserPsycId(self, u_id):
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
        blg = db.blog.select()\
                     .join(db.psychologist, JOIN_INNER, db.blog.psyc == db.psychologist.psyc_id)\
                     .join(db.user, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                     .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                     .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                     .where(db.user.active & (db.role.role_nm == 'psyc') & (db.psychologist.psyc_id == psyc_id))\
                     .order_by(db.blog.updt_dtm.desc())
        return blg

    def getAvatar(self, psyc_id):
        psyc = db.psychologist.get(db.psychologist.psyc_id == psyc_id)
        if psyc.photo is None or psyc.photo == '':
            return '/static/noavatar.png'

        public_id, version = psyc.photo.split('#')

        return cloudinary.CloudinaryImage(public_id, version=version).build_url()

    def updateAvatar(self, psyc_id, avatar_file):
        if not self.allowed_file(avatar_file.filename):
            return False

        response = cloudinary.uploader.upload(avatar_file)
        image_descriptor = response['public_id'] + '#' + str(response['version'])

        p = db.psychologist.get(db.psychologist.psyc_id == psyc_id)
        p.photo = image_descriptor
        p.save()

        return True

    def getPsycId(self, u_id):
        results = db.user.select(db.psychologist.psyc_id)\
                        .join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user)\
                        .join(db.role, JOIN_INNER, db.user_roles.role == db.role.role_id)\
                        .join(db.psychologist, JOIN_INNER, db.psychologist.user == db.user.user_id)\
                        .where(db.user.active & (db.user.user_id == u_id) & (db.role.role_nm == 'psyc')).tuples()
        if len(results) == 0:
            return -1
        psyc_id = results[0][0]
        return psyc_id

    def createBlogPost(self, u_id, psyc_id, text):
        now = datetime.datetime.now()
        blog_post = db.blog(psyc=psyc_id,
                            text=text,
                            crea_dtm=now,
                            user_id_upd=u_id,
                            updt_dtm=now,
                            void_ind='n')
        blog_post.save()

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

    def getChildren(self, user_id): #ignore this for now, it is a bad attempt at something
        c = db.child.select().where(db.child.user == user_id)
        return c

    def exists(self, contact_id, field):
        c = db.contact.select().where(db.contact.contact_id == contact_id)
        if field == 'phone_no' and c.phone_no.exists():
            return True
        elif field == 'address_1' and c.address_1.exists():
            return True
        elif field == 'address_2' and c.address_2.exists():
            return True
        elif field == 'city' and c.city.exists():
            return True
        elif field == 'providence' and c.providence.exists():
            return True
        elif field == 'zip' and c.zip.exists():
            return True
        else:
            return False

    def contactID(self, user_id):
        try:
            c = db.contact.select().where(db.contact.user_id == user_id).get()
        except DoesNotExist:
            c = None
        return c

    def getContact(self, user_id):
        c = db.contact.select().where(db.contact.user == user_id)
        return c

    def updateContact(self, user_id, contact_id, phone_no, address_1, address_2, city, providence, zip):
        try:
            c = db.contact.select().where(db.contact.user_id == user_id).get()
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

    #End of Gabe's code

    #Nolan's Code

    def getVerifiedChildren(self):
        children = []
        for consultation in db.consultation.select():
            if consultation.approved == "y" and consultation.paid == "n":
                children += consultation.child

        return children

    #End Nolan's Code

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
        return slider_tag, slider_desc


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
