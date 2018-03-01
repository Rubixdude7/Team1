import calendar

from flask import Markup
import bleach
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

    def addQuestion(self, question2, user):
        q = db.questions(question=question2, user_id_crea=user, crea_dtm=datetime.datetime.now())
        q.save()

    def checkNewQuestions(self, child):
        child = db.child.get(db.child.child_id == child)
        x = child.q_comp_dtm
        questionsUpdated = db.questions.select().where(db.questions.crea_dtm > x)

        return questionsUpdated

    def addQuestionAnswers(self, questionAnswer, user, q_id, childId):
        # Begin Brody
        '''
            This should now prevent additional rows from being
            added unnecessarily, i.e., the answer didn't change for this kid, for this question
        '''
        alreadyExists = query.getAnswer(self, q_id, childId)
        if alreadyExists is None:
            # Begin Jared
            current = db.child.get(db.child.child_id == childId)
            current.q_comp_dtm = datetime.datetime.now()
            current.save()

            q = db.question_answers(answer=questionAnswer, user_id_crea=user, crea_dtm=datetime.datetime.now(), q=q_id,
                                    child=childId, void_ind='n')
            q.save()
            # End Jared
        elif alreadyExists == questionAnswer:
            print("Answer already exists and didn't change!")
        else:
            print("Updating answer")
            query.voidAnswer(self, q_id, childId)
            # Begin Jared
            current = db.child.get(db.child.child_id == childId)
            current.q_comp_dtm = datetime.datetime.now()
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

    def getAllQuestions(self):
        questions = db.questions.select().where(db.questions.void_ind != 'd')
        return questions

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
            return c
        except:
            return None

    def getAnswer(self, question_id, child_id):
        try:
            a = db.question_answers.get(db.question_answers.q == question_id, db.question_answers.child == child_id, db.question_answers.void_ind == 'n')
            print(a.answer)
            return a.answer
        except:
            return None
    # End Brody's code

# Start Jason's code

    def getAllUsers(self, page_num, num_of_pages):
        users = db.user.select().where(db.user.active).join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user).order_by(db.user_roles.role).paginate(page_num, num_of_pages)
        return users

    def getSearchedUsers(self, search, page_num, num_of_pages):
        users = db.user.select().where(db.user.active & db.user.email.contains(search)).join(db.user_roles, JOIN_INNER, db.user.user_id == db.user_roles.user).order_by(db.user_roles.role).paginate(page_num, num_of_pages)

        # users = db.user.select().where(db.user.active & db.user.email.contains(search)).paginate(page_num, num_of_pages)
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
    
    def getAllBlogPosts(self, page_num, items_per_page):
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

    def createBlogPost(self, u_id, psyc_id, subject, text):
        text = bleach.clean(text)
        now = datetime.datetime.now()
        blog_post = db.blog(psyc=psyc_id,
                            subject=subject,
                            text=text,
                            crea_dtm=now,
                            user_id_upd=u_id,
                            updt_dtm=now,
                            void_ind='n')
        blog_post.save()

    def updateQualifications(self, psyc_id, qualifications):
        psyc = db.psychologist.select().where(db.psychologist.psyc_id == psyc_id).get()
        psyc.qualifications = qualifications
        psyc.save()

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
        
    def getAvailabilities(self, psyc_id):
        tuples = db.calendar.select(db.calendar.cal_id, db.calendar.time_st, db.calendar.time_end, db.day_typ_cd.day_typ_cd)\
                            .join(db.psychologist, JOIN_INNER, db.psychologist.psyc_id == db.calendar.psyc)\
                            .join(db.day_typ_cd, JOIN_INNER, db.calendar.day_typ_cd == db.day_typ_cd.day_typ_cd)\
                            .where((db.psychologist.psyc_id == psyc_id) & (db.calendar.void_ind == 'n'))\
                            .tuples()
        return [{
            'avail_id': t[0],
            'time_st': t[1],
            'time_end': t[2],
            'weekday': t[3]
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
        
    def getWeekDays(self):
        wkds = db.day_typ_cd.select()
        d = {}
        for wkd in wkds:
            d[wkd.day_typ_cd] = wkd.day
        return d

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

    def get_consultation(self):
        psycs = db.psychologist.select(db.psychologist.psyc_id, db.user.first_name, db.user.last_name).join(db.user, JOIN_INNER, db.user.user_id == db.psychologist.user).tuples()
        psycs = list(psycs)

        len_fee = db.consultation_length.select(db.consultation_length.cnslt_len_id, db.consultation_length.length, db.consultation_fee.fee).where(db.consultation_length.void_ind == 'n').join(db.consultation_fee, JOIN_INNER, db.consultation_length.cnslt_fee == db.consultation_fee.cnslt_fee_id).tuples()
        len_fee = list(len_fee)

        return psycs, len_fee

    def get_psyc_cnslt(self, cnslt):

        if cnslt.get('psyc', None) == '-1':
            time = cnslt.get('date', None) + " " + cnslt.get('hour', None) + ":" + cnslt.get('min', None)
            time_st = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
            time_end = time_st + datetime.timedelta(hours=float(cnslt.get('len_fee', None)))
            taken_times = db.consult_time.select()\
                .where(((db.consult_time.time_st <= time_st) & (db.consult_time.time_end <= time_end) & (time_st <= db.consult_time.time_end))
                       | ((db.consult_time.time_st >= time_st) & (db.consult_time.time_end >= time_end) & (time_end >= db.consult_time.time_st))
                       | ((db.consult_time.time_st <= time_st) & (db.consult_time.time_end >= time_end))
                       | ((db.consult_time.time_st >= time_st) & (db.consult_time.time_end <= time_end))).tuples()

            taken_times = list(taken_times)

            #if no conflicts
            if len(taken_times) == 0:
                day_of_week = calendar.day_name[time_st.weekday()]
                cal = db.calendar.select().where((db.calendar.time_st <= time_st.time()) & (db.calendar.time_end >= time_end.time()) & (db.calendar.void_ind == 'n'))\
                    .join(db.day_typ_cd, JOIN_INNER, (db.day_typ_cd.day == day_of_week) & (db.day_typ_cd.day_typ_cd == db.calendar.day_typ_cd)).tuples()
                cal = list(cal)

                psycs = []
                for c in cal:
                    psyc = db.psychologist.select(db.psychologist.psyc_id, db.psychologist.photo, db.user.first_name, db.user.last_name).where(db.psychologist.psyc_id == c[1]).join(db.user, JOIN_INNER, db.user.user_id == db.psychologist.user).tuples()
                    print(list(psyc[0]))
                    psyc = list(psyc[0])
                    public_id, version = psyc[1].split('#')
                    link = cloudinary.CloudinaryImage(public_id, version=version).build_url()
                    print(psyc)
                    psyc[1] = link

                    book = dict()
                    book['child_id'] = cnslt.get('child_id', None)
                    fee = db.consultation_fee.select(db.consultation_fee.fee).where(db.consultation_fee.void_ind == 'n').join(db.consultation_length, JOIN_INNER, (db.consultation_length.cnslt_fee == db.consultation_fee.cnslt_fee_id) & (db.consultation_length == cnslt.get('len_fee', None))).tuples()
                    print(fee)
                    book['fee'] = fee
                    book['len'] = cnslt.get('len_fee', None)
                    book['psyc_id'] = psyc[0]
                    book['time_st'] = time_st
                    book['time_end'] = time_end
                    psyc.append(book)

                    psycs.append(psyc)
                print(psycs)

        return None


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
