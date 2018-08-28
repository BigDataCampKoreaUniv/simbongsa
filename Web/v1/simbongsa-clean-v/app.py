from flask import Flask, render_template,request, redirect, url_for, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_security.forms import RegisterForm
from flask_security.views import _ctx, register_user, current_user
from flask_sqlalchemy import SQLAlchemy
import json
import sqlite3
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)


# Database 생성
app.config['DEBUG'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '심봉사'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECRET_KEY'] = '심봉사'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bongsa.db'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# app.config.update({'SECRET_KEY':'김성제'})
moment = Moment(app)
db = SQLAlchemy(app)
admin = Admin(app, name='봉사왕심봉사', template_mode='bootstrap3')

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


#
# 전역 변수 선언
#
# user_list = 유저 매트릭스
user_list=[]
# vol_list = 봉사활동 매트릭스
vol_list = []
# vol_content = 봉사활동 정보들
vol_content = []
# vol_latlng = 봉사활동 별 위도, 경도 값
vol_latlng = []
# 유사도 결과값
new_list_sub=[]
more_recommend = []
# 첫번째 지도 결과 값
first_city_list = []
# 전공이 같은 애들이 좋아요 누른 것들
t_list = []
# 첫 번째 선호 지역
first_city=''


similar_star_rate = []
category_names = []
likes_bool = []
more_categories = []
total_categories = []

major_similarity = []


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


# User Model 생성
class User(db.Model, UserMixin):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    sex = db.Column(db.Integer())
    grade = db.Column(db.Integer())
    university = db.Column(db.String(255))
    majoring = db.Column(db.String(255))
    # for i in range(1,21):
    #     locals()[f"volun{i}"] = db.Column(db.Integer())
    prefer_bloc1 = db.Column(db.String(255))
    prefer_sloc1 = db.Column(db.String(255))
    prefer_bloc2 = db.Column(db.String(255))
    prefer_sloc2 = db.Column(db.String(255))
    prefer_bloc3 = db.Column(db.String(255))
    prefer_sloc3 = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    # fore_id = db.relationship("User_category", backref='user', lazy=True)
    # fore_id2 = db.relationship("Like", backref='user1', lazy=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def to_tuple(self):
        return (self.id, self.email, self.password, self.sex, self.grade, self.university,
                self.majoring, self.prefer_bloc1, self.prefer_sloc1, self.prefer_bloc2, self.prefer_sloc2,
                self.prefer_sloc3, self.prefer_bloc3)


class User_category(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    category_life = db.Column(db.Float())
    category_world = db.Column(db.Float())
    category_environment = db.Column(db.Float())
    category_human = db.Column(db.Float())
    category_disaster = db.Column(db.Float())
    category_country = db.Column(db.Float())
    category_home = db.Column(db.Float())
    category_medic = db.Column(db.Float())
    category_education = db.Column(db.Float())
    category_administration = db.Column(db.Float())
    category_consulting = db.Column(db.Float())
    category_culture = db.Column(db.Float())
    category_physical = db.Column(db.Float())
    category_history = db.Column(db.Float())
    category_circles = db.Column(db.Float())
    category_travel = db.Column(db.Float())
    category_marketing = db.Column(db.Float())
    category_social = db.Column(db.Float())
    category_plan = db.Column(db.Float())
    category_language = db.Column(db.Float())
    category_scene = db.Column(db.Float())
    category_etc = db.Column(db.Float())
    recruit_disabled = db.Column(db.Float())
    recruit_oldman = db.Column(db.Float())
    recruit_foreigner = db.Column(db.Float())
    recruit_homeless = db.Column(db.Float())
    recruit_multiculture = db.Column(db.Float())
    recruit_worker = db.Column(db.Float())
    recruit_baby = db.Column(db.Float())
    recruit_women = db.Column(db.Float())
    recruit_zzokbang = db.Column(db.Float())
    recruit_teenager = db.Column(db.Float())
    recruit_nation = db.Column(db.Float())

    def to_tuple(self):
        return (self.id, self.category_life, self.category_world,
                self.category_environment, self.category_human, self.category_disaster, self.category_country,
                self.category_home, self.category_medic, self.category_education, self.category_administration,
                self.category_consulting, self.category_culture, self.category_physical, self.category_history,
                self.category_circles, self.category_travel, self.category_marketing, self.category_social,
                self.category_plan, self.category_language, self.category_scene, self.category_etc, self.recruit_disabled,
                self.recruit_oldman, self.recruit_foreigner, self.recruit_homeless,self.recruit_multiculture,
                self.recruit_worker, self.recruit_baby, self.recruit_women, self.recruit_zzokbang, self.recruit_teenager,
                self.recruit_nation)


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    recruit_office = db.Column(db.String())
    place = db.Column(db.String())
    contents = db.Column(db.String())
    recruit_startdate = db.Column(db.Integer)
    recruit_enddate = db.Column(db.Integer)
    activity_date = db.Column(db.String())
    category_life = db.Column(db.Integer)
    category_world = db.Column(db.Integer)
    category_environment = db.Column(db.Integer)
    category_human = db.Column(db.Integer)
    category_disaster = db.Column(db.Integer)
    category_country = db.Column(db.Integer)
    category_home = db.Column(db.Integer)
    category_medic = db.Column(db.Integer)
    category_education = db.Column(db.Integer)
    category_administration = db.Column(db.Integer)
    category_consulting = db.Column(db.Integer)
    category_culture = db.Column(db.Integer)
    category_physical = db.Column(db.Integer)
    category_history = db.Column(db.Integer)
    category_circles = db.Column(db.Integer)
    category_travel = db.Column(db.Integer)
    category_marketing = db.Column(db.Integer)
    category_social = db.Column(db.Integer)
    category_plan = db.Column(db.Integer)
    category_language = db.Column(db.Integer)
    category_scene = db.Column(db.Integer)
    category_etc = db.Column(db.Integer)
    recruit_disabled = db.Column(db.Integer)
    recruit_oldman = db.Column(db.Integer)
    recruit_foreigner = db.Column(db.Integer)
    recruit_homeless = db.Column(db.Integer)
    recruit_multiculture = db.Column(db.Integer)
    recruit_worker = db.Column(db.Integer)
    recruit_baby = db.Column(db.Integer)
    recruit_women = db.Column(db.Integer)
    recruit_zzokbang = db.Column(db.Integer)
    recruit_teenager = db.Column(db.Integer)
    recruit_nation = db.Column(db.Integer)
    city1 = db.Column(db.String())
    city2 = db.Column(db.String())
    address = db.Column(db.String())
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    # volfor_id = db.relationship("Like", backref='volun', lazy=True)

    def to_tuple(self):
        return (self.id, self.title, self.recruit_office, self.place, self.contents, self.recruit_startdate,
                self.recruit_enddate, self.activity_date, self.category_life, self.category_world,
                self.category_environment, self.category_human, self.category_disaster, self.category_country,
                self.category_home, self.category_medic, self.category_education, self.category_administration,
                self.category_consulting, self.category_culture, self.category_physical, self.category_history,
                self.category_circles, self.category_travel, self.category_marketing, self.category_social,
                self.category_plan, self.category_language, self.category_scene, self.category_etc, self.recruit_disabled,
                self.recruit_oldman, self.recruit_foreigner, self.recruit_homeless,self.recruit_multiculture,
                self.recruit_worker, self.recruit_baby, self.recruit_women, self.recruit_zzokbang, self.recruit_teenager,
                self.recruit_nation, self.city1, self.city2, self.address, self.latitude, self.longitude)


class Like(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), primary_key= True, nullable=False)


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User_category, db.session))
admin.add_view(ModelView(Volunteer, db.session))
admin.add_view(ModelView(Like, db.session))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)  # Security 기능 확장 위함

univer = ""
major = ""


#@app.before_first_request # 초기화할때
def create_user():
    db.create_all()
    user_datastore.create_user(email='sungje5957@gmail.com', password='pw')
    db.session.commit()





def classification(categories):
    category_num = 22
    receiver_cate_num = 11
    category_toTag = []

    category_names = ''
    category_receivers = ''

    category_dict = {0:'생활편의', 1:'국제협력', 2:'환경', 3:'인권', 4:'재해/재난', 5:'농어촌', 6:'주거환경', 7:'보건의료',
                     8:'교육', 9:'행정지원', 10:'상담', 11:'문화', 12:'체육', 13:'역사', 14:'동아리', 15:'여행', 16:'홍보',
                    17:'사회공헌', 18:'기획', 19:'언어', 20:'현장', 21:'기타'}
    receiver_dict = {0:'장애인', 1:'노인', 2:'외국인', 3:'노숙인', 4:'다문화가정', 5:'노동자', 6:'유아', 7:'여성', 8:'쪽방촌', 9:'청소년', 10:'지역사회'}

    #생활 편의	국제 협력	환경	인권	재해/재난	농어촌	주거 환경	보건 의료	교육	행정 지원	상담
    # 문화	체육	역사	동아리	여행	홍보	사회공헌	기획	언어	현장	기타
    # 장애인	노인	외국인	노숙인	다문화가정	노동자	유아	여성	쪽방촌	청소년	지역사회

    for i in range(category_num):
        if categories[i] > 0:
            category_toTag.append(category_dict[i])
            category_names += category_dict[i] + ', '
        if i == category_num - 1:  # 맨마지막 index일 때
            if category_names[-2:] == ', ':
                category_names = category_names[:-2]

    for i in range(receiver_cate_num):
        if categories[category_num+i] > 0:
            category_toTag.append(receiver_dict[i])
            category_receivers += receiver_dict[i] + ', '
        if i == receiver_cate_num-1:  # 맨마지막 index일 때 맨 뒤에 ','빼기
            if category_receivers[-2:] == ', ':
                category_receivers = category_receivers[:-2]

    return category_names, category_receivers, category_toTag  # 문자열로 return



# main에 추천부에서 content제목 위에 벡터 값이 가장 큰 분야 1개 return하기
def max_classification(categories):
    category_num = 22

    category_names = ''

    category_dict = {0:'생활편의', 1:'국제협력', 2:'환경', 3:'인권', 4:'재해/재난', 5:'농어촌', 6:'주거환경', 7:'보건의료',
                     8:'교육', 9:'행정지원', 10:'상담', 11:'문화', 12:'체육', 13:'역사', 14:'동아리', 15:'여행', 16:'홍보',
                    17:'사회공헌', 18:'기획', 19:'언어', 20:'현장', 21:'기타'}

    max_cnt = 0
    for i in range(category_num):
        if categories[i] > 0 and categories[i] > max_cnt:
            category_names = category_dict[i]
            max_cnt = categories[i]

    return category_names  # 문자열로 return

# db에 user가 해당 content를 이미 좋아요 했는지 아닌지 체크  -> javascript에 전달함
def already_liked(user_id, content_id):
    # conn = sqlite3.connect('bongsa.db')
    # cur = conn.cursor()
    # execute_stm = "select * from likes where user_id=" + str(user_id) + " and content_id=" + str(content_id)
    # cur.execute(execute_stm)
    # res = cur.fetchone()
    # conn.close()

    """modified to sqlalchemy"""
    a = Like.query.all()
    res = []
    for i in range(len(a)):
        if a[i].user_id == user_id and a[i].content_id == content_id:
            res = [a[i].user_id, a[i].content_id]


    if len(res) ==0:  # db에 없으면 false
        return 'false'
    else:              # db에 있으면 true
        return 'true'

def similar_star(similarity):
    if similarity >= 0.8:
        return [5,0]
    elif similarity >= 0.6:
        return [4,1]
    elif similarity >= 0.4:
        return [3,2]
    elif similarity >= 0.2:
        return [2,3]
    elif similarity == 0:
        return [0,5]
    else:
        return [1,4]


"""modified"""
# 유사도 상위 4개 content 추출
def maxuser(index, user_matrix, content_matrix, latlng):
    global more_recommend, new_list_sub, more_categories
    new_list_sub = []
    more_recommend = []
    # 코사인 유사도기법을 사용하면 결과 값이 튜플로 나옴
    # 튜플 -> list로 변경시켜주고,
    # sort를 위해 index를 추가해준다.
    reverse_cos = cosine_similarity(user_matrix, content_matrix)
    reverse_list = reverse_cos[index].tolist()

    new_list = []
    for i in range(len(reverse_list)):
        new_list.append([i, latlng[i][1], latlng[i][2], reverse_list[i]])
        # new_list.append([reverse_list[i], i, latlng[i][1], latlng[i][2]])
    new_list = sorted(new_list, reverse=True, key=lambda nlist: nlist[3])
    #    new_list.sort(reverse=True)
    # 상위 5개만 뽑아라
    # print(new_list)
    # 상위 5개만 뽑아라d
    for i in range(0, 4):
        sub = []
        for j in range(0, 4):
            sub.append(new_list[i][j])
        new_list_sub.append(sub)
    # print(new_list_sub[:5])

    # 더보기를 위한 리스트

    for i in range(0, 100):
        sub = []
        for j in range(0, 4):
            sub.append(new_list[i][j])
        more_recommend.append(sub)
    # print(len(more_recommend),'up',more_recommend)


    more_categories = []

    print('more_rec',more_recommend)
    # volunquery = Volunteer.query.all()
    # print('vol_list',vol_list)
    for i in range(len(more_recommend)):
        more_categories.append(max_classification(vol_list[i]))
    #     row = select * from volunteer where id=more_recomment[i][0]
    #     more_categories.append(max_classification(row[8:-2]))
    # temp_city_list.append(volun_city[i].to_tuple())
    # for i in range(len(volunquery)):
    #     if volunteer[i]
        # row_list = list(volunquery[i].to_tuple()[8:30])
        # row_content = list(volunquery[i].to_tuple()[0:8])
        # vol_list.append(row_list)
        # vol_content.append(row_content)

    # print('newlistsub',new_list_sub)
    return new_list_sub[:4]
    # return new_list[:4]



def GeoCoordinates(addr):
    import os
    import sys
    import urllib.request

    client_id = "ZbNWupFQAk_cmBAmLstr"
    client_secret = "5_knjXBU5Z"

    encText = urllib.parse.quote(addr)
    url = "https://openapi.naver.com/v1/map/geocode?query=" + encText # json 결과
    # url = "https://openapi.naver.com/v1/map/geocode.xml?query=" + encText # xml 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        mystr = response_body.decode('utf-8')
        mystr = mystr.replace('true',"True")
        mystr = mystr.replace('false',"False")
        mydic = eval(mystr)
    else:
        print("Error Code:" + rescode)
    return mydic


@app.route('/mypage', methods=['GET', 'POST'] )
def mypage():
    user_id = current_user.get_id()
    # print(type(user_id))
    # user가 좋아요 한 Content ID가져오기
    userLike = Like.query.all()
    temp_list = [] # volunteer Content id 임시저장
    for i in range(len(userLike)):
        if userLike[i].user_id == int(user_id):
            temp_list.append(userLike[i].content_id)

    # volunteer content 가져오기
    volunContents = Volunteer.query.all()
    volun_list = []
    count = 1
    for j in temp_list:
        volun_list.append([j, volunContents[j].title, count])
        count += 1
    # print(volun_list)
    return render_template('mypage.html', contentlike=volun_list)

@app.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('aboutus.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/register/search', methods=['GET', 'POST'])
def searchuniv():
    import pandas as pd
    univ_data = pd.read_csv(r'static\\대학현황.csv', engine='python',
                            encoding='utf-8-sig')

    univName = pd.Series(univ_data['학교명'].unique())
    univDict = {}

    if request.method == 'POST':

        if request.form['btn'] == "대학교검색":

            univ = request.form['search']

            for univ_name in univName:
                if univ in univ_name:
                    univDict[univ_name] = list(univ_data[univ_data['학교명'] == univ_name]['학부·과(전공)명'])

        if request.form['btn'] == "제출":
            global univer, major
            univer = request.form['slct1']
            major = request.form['slct2']

    return render_template("search.html", univDict=univDict)


@app.route('/register/', methods=['GET', 'POST'])
# @anonymous_user_required
def register_users():
    register_user_form = RegisterForm()

    if request.method == 'POST':
        if register_user_form.validate_on_submit():
            user = register_user(**register_user_form.to_dict())
            user.sex = request.form['mf']
            user.grade = request.form['grade']

            # if request.form.get('volun1', None):
            #     user.volun1 = 1
            # else:
            #     user.volun1 = 0
            #
            # if request.form.get('volun2', None):
            #     user.volun2 = 1
            # else:
            #     user.volun2 = 0
            #
            # if request.form.get('volun3', None):
            #     user.volun3 = 1
            # else:
            #     user.volun3 = 0
            #
            # if request.form.get('volun4', None):
            #     user.volun4 = 1
            # else:
            #     user.volun4 = 0
            #
            # if request.form.get('volun5', None):
            #     user.volun5 = 1
            # else:
            #     user.volun5 = 0
            #
            # if request.form.get('volun6', None):
            #     user.volun6 = 1
            # else:
            #     user.volun6 = 0
            #
            # if request.form.get('volun7', None):
            #     user.volun7 = 1
            # else:
            #     user.volun7 = 0
            #
            # if request.form.get('volun8', None):
            #     user.volun8 = 1
            # else:
            #     user.volun8 = 0
            #
            # if request.form.get('volun9', None):
            #     user.volun9 = 1
            # else:
            #     user.volun9 = 0
            #
            # if request.form.get('volun10', None):
            #     user.volun10 = 1
            # else:
            #     user.volun10 = 0
            # if request.form.get('volun11', None):
            #     user.volun11 = 1
            # else:
            #     user.volun11 = 0
            # if request.form.get('volun12', None):
            #     user.volun12 = 1
            # else:
            #     user.volun12 = 0
            # if request.form.get('volun13', None):
            #     user.volun13 = 1
            # else:
            #     user.volun13 = 0
            # if request.form.get('volun14', None):
            #     user.volun14 = 1
            # else:
            #     user.volun14 = 0
            # if request.form.get('volun15', None):
            #     user.volun15 = 1
            # else:
            #     user.volun15= 0
            # if request.form.get('volun16', None):
            #     user.volun16 = 1
            # else:
            #     user.volun16 = 0
            # if request.form.get('volun17', None):
            #     user.volun17 = 1
            # else:
            #     user.volun17 = 0
            # if request.form.get('volun18', None):
            #     user.volun18 = 1
            # else:
            #     user.volun18 = 0
            # if request.form.get('volun19', None):
            #     user.volun19 = 1
            # else:
            #     user.volun19 = 0
            # if request.form.get('volun20', None):
            #     user.volun20 = 1
            # else:
            #     user.volun20 = 0

            volun1 = 1 if request.form.get('volun1', None) else 0
            volun2 = 1 if request.form.get('volun2', None) else 0
            volun3 = 1 if request.form.get('volun3', None) else 0
            volun4 = 1 if request.form.get('volun4', None) else 0
            volun5 = 1 if request.form.get('volun5', None) else 0
            volun6 = 1 if request.form.get('volun6', None) else 0
            volun7 = 1 if request.form.get('volun7', None) else 0
            volun8 = 1 if request.form.get('volun8', None) else 0
            volun9 = 1 if request.form.get('volun9', None) else 0
            volun10 = 1 if request.form.get('volun10', None) else 0
            volun11 = 1 if request.form.get('volun11', None) else 0
            volun12 = 1 if request.form.get('volun12', None) else 0
            volun13 = 1 if request.form.get('volun13', None) else 0
            volun14 = 1 if request.form.get('volun14', None) else 0
            volun15 = 1 if request.form.get('volun15', None) else 0
            volun16 = 1 if request.form.get('volun16', None) else 0
            volun17 = 1 if request.form.get('volun17', None) else 0
            volun18 = 1 if request.form.get('volun18', None) else 0
            volun19 = 1 if request.form.get('volun19', None) else 0
            volun20 = 1 if request.form.get('volun20', None) else 0
            volun21 = 1 if request.form.get('volun21', None) else 0
            volun22 = 1 if request.form.get('volun22', None) else 0

            recruit1 = 1 if request.form.get('recruit1', None) else 0
            recruit2 = 1 if request.form.get('recruit2', None) else 0
            recruit3 = 1 if request.form.get('recruit3', None) else 0
            recruit4 = 1 if request.form.get('recruit4', None) else 0
            recruit5 = 1 if request.form.get('recruit5', None) else 0
            recruit6 = 1 if request.form.get('recruit6', None) else 0
            recruit7 = 1 if request.form.get('recruit7', None) else 0
            recruit8 = 1 if request.form.get('recruit8', None) else 0
            recruit9 = 1 if request.form.get('recruit9', None) else 0
            recruit10 = 1 if request.form.get('recruit10', None) else 0
            recruit11 = 1 if request.form.get('recruit11', None) else 0

            temp_category = User_category()
            temp_category.id = user.id
            temp_category.category_life = volun1
            temp_category.category_world = volun2
            temp_category.category_environment = volun3
            temp_category.category_human = volun4
            temp_category.category_disaster = volun5
            temp_category.category_country = volun6
            temp_category.category_home = volun7
            temp_category.category_medic = volun8
            temp_category.category_education = volun9
            temp_category.category_administration = volun10
            temp_category.category_consulting = volun11
            temp_category.category_culture = volun12
            temp_category.category_physical = volun13
            temp_category.category_history = volun14
            temp_category.category_circles = volun15
            temp_category.category_travel = volun16
            temp_category.category_marketing = volun17
            temp_category.category_social = volun18
            temp_category.category_plan = volun19
            temp_category.category_language = volun20
            temp_category.category_scene = volun21
            temp_category.category_etc = volun22
            temp_category.recruit_disabled = recruit1
            temp_category.recruit_oldman= recruit2
            temp_category.recruit_foreigner = recruit3
            temp_category.recruit_homeless = recruit4
            temp_category.recruit_multiculture = recruit5
            temp_category.recruit_worker = recruit6
            temp_category.recruit_baby = recruit7
            temp_category.recruit_women = recruit8
            temp_category.recruit_zzokbang = recruit9
            temp_category.recruit_teenager = recruit10
            temp_category.recruit_nation = recruit11

            user.prefer_bloc1 = request.form['category']
            user.prefer_sloc1 = request.form['choices']
            user.prefer_bloc2 = request.form['category1']
            user.prefer_sloc2 = request.form['choices1']
            user.prefer_bloc3 = request.form['category2']
            user.prefer_sloc3 = request.form['choices2']

            user.university = request.form['university']
            user.majoring = request.form['majoring']

            register_user_form.user = user
            db.session.add(temp_category)
            db.session.commit()

            global univer, major
            major = ""
            univer = ""
            return user_detail()
#            return redirect(url_for('user_detail'))  # register가 완성되면 초기페이지로
        else:
            flash(register_user_form.errors, 'info')
            return render_template("register.html", register_user_form=register_user_form, **_ctx('register'))
    else:
        return render_template("register.html", register_user_form=register_user_form, univer=univer, major=major)



# def major_recommend(user_id):
#     conn = sqlite3.connect('bongsa.db')
#     cur = conn.cursor()
#
#     vol_list=[]
#     vol_content=[]
#     cur.execute("select majoring from user where id="+str(user_id))
#     vol_row = cur.fetchone()
#
#     conn.close()
#     print(vol_row)


#
# @app.route('/')
# def main_guest():
#     return render_template('guest_main.html')




# main_page 유사도 기반 유저에게 컨텐츠 추천
@app.route('/', methods=['GET','POST'])
def user_detail():
    global vol_content, vol_list, vol_latlng,similar_star_rate, category_names, likes_bool, t_list,first_city,first_city_list, major_similarity
#    user_id = current_user.get_id()
    user_id = 0
    if not user_id:
        user_id = 0 #default
    else:
        user_id = int(user_id)  #str->int

    # major_recommend(user_id)
    # get_add = GeoCoordinates('서울 중구 덕수궁길 15')
#    print(get_add['result']['items'][0]['point']['x'], get_add['result']['items'][0]['point']['y'])

#    user_id = 3   # temporary
    # db 연결
    conn = sqlite3.connect('bongsa.db')
    cur = conn.cursor()
    # #
    #   컨텐츠 카테고리 매트릭스 만들기
    #
    vol_list=[]
    vol_content=[]
#     cur.execute("select * from volunteer")
#     vol_row = cur.fetchall()
#
#     for i in range(len(vol_row)):
#         row_list = list(vol_row[i][8:30])
#         row_content = list(vol_row[i][0:8])
#         vol_list.append(row_list)
#         vol_content.append(row_content)

    volunquery = Volunteer.query.all()
    for i in range(len(volunquery)):
        row_list = list(volunquery[i].to_tuple()[8:30])
        row_content = list(volunquery[i].to_tuple()[0:8])
        vol_list.append(row_list)
        vol_content.append(row_content)


    vol_latlng = []
    # cur.execute("select id,latitude,longitude from volunteer")
    # vol_row = cur.fetchall()
    vol_row = []
    latquery = Volunteer.query.all()
    for i in range(len(latquery)):
        temp_vol = latquery[i].to_tuple()
        temp = []
        temp.append(temp_vol[0])
        temp.append(temp_vol[-2])
        temp.append(temp_vol[-1])
        vol_row.append(temp)
        # row_list = list(latquery[i].to_tuple()[8:30])
        # row_content = list(volunquery[i].to_tuple()[0:8])
        # vol_list.append(row_list)
        # vol_content.append(row_content)


    for i in range(len(vol_row)):
        row_latlng = list(vol_row[i][0:3])
        vol_latlng.append(row_latlng)

    #
    #   유저 카테고리 매트릭스 만들기
    #
    # cur.execute("select * from user_category")  # content_id에 해당하는 컨텐츠 가져오기
    # user_row = cur.fetchall()
    #
    # user_list = []
    #
    # # 유저카테고리 1:23
    # # 튜플인 데이터를 유저매트릭스에 저장하기
    # for i in range(len(user_row)):
    #     row_list=list(user_row[i][1:23])
    #     user_list.append(row_list)
    """modified to sqlalchemy"""
    usercate = User_category.query.all()
    # user_list = []
    for i in range(len(usercate)):
        row_list = list(usercate[i].to_tuple()[1:23])
        user_list.append(row_list)


    # 유사도 별 갯수

    similar_list = maxuser(int(user_id), user_list, vol_list, vol_latlng)
    #
    # 유저의 첫 번째 선호도 지역 받아오기
    #
    # cur.execute("select prefer_sloc1 from user where id=" + str(user_id)) # clear
    # first_city_row = cur.fetchone()
    # first_city = first_city_row[0]

    # first_city = "" # 일단 str으로 선언
    user_prefer1 = User.query.all() # User query 가져오고
    for i in range(len(user_prefer1)):
        if user_prefer1[i].id == int(user_id):
            first_city = user_prefer1[i].prefer_sloc1 # 기초지방자치단체 저장
    # print("line:707; first_city는", first_city)


    # cur.execute("select * from volunteer where city2='" + first_city + "'")
    # first_city_row = cur.fetchall()

    temp_city_list = [] # 임시 리스트 생성
    first_city_list = []
    #
    volun_city = Volunteer.query.all()
    for i in range(len(volun_city)):
        if volun_city[i].city2 == first_city:
            temp_city_list.append(volun_city[i].to_tuple())
    # print("first_city_list", first_city_list)

    for i in range(len(temp_city_list)):
        row_list = list(temp_city_list[i][44:])
        first_city_list.append([temp_city_list[i][0], row_list[0], row_list[1]])

    first_city4 = first_city_list[:8]
    # print("first_city4는", first_city4)
    total_list = []
    for i in range(len(similar_list)):
        total_list.append(similar_list[i])

    for i in range(len(first_city4)):
        total_list.append(first_city4[i])


    # print('total_list',total_list[:5])
    # print('similar',similar_list)

    # print("@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(total_list)
    # print("@@@@@@@@@@@@@@@@@@@@@@@@")

    # # 유저의 전공 알아오기!
    # cur.execute("select majoring from user where id="+str(user_id))
    # user_major_row = cur.fetchone()
    # user_major = user_major_row[0]
    #
    # # 유저의 전공에 해당하는 유저의 좋아요한 페이지 받아오기
    # cur.execute("select user_id,content_id from "
    #             "(select * from user u, like l where u.id = l.user_id) where majoring = '"+user_major+"'")
    # test_row = cur.fetchall()

    # # 유저의 전공 알아오기!
    user_major = ""
    getUserMajor = User.query.all()
    for i in range(len(getUserMajor)):
        if getUserMajor[i].id == user_id:
            user_major = getUserMajor[i].majoring
    print(user_major)

    # 유저의 전공에 해당하는 유저의 좋아요한 페이지 받아오기
    getLike = Like.query.all()
    getUserid = User.query.all()

    tempSameMajor = []
    for i in range(len(getUserid)):
        if getUserid[i].majoring == user_major:
            tempSameMajor.append(getUserid[i].id)
    # print(tempSameMajor)

    print('temp',tempSameMajor)
    # print(user_id)
    # uidcid = []
    test_row = []
    for k in tempSameMajor:
        for j in range(len(getLike)):
            if getLike[j].user_id == k:
                test_row.append([getLike[j].user_id, getLike[j].content_id])
    # print(uidcid)
    print('test_row', test_row)

    t_list = []
    for i in range(len(test_row)):
        tt = list(test_row[i])
        t_list.append(tt)
    # print("##############################")
    # print(t_list)
    # print("##############################")

    print(t_list)
    temp_list = []
    for i in range(len(t_list)):
        temp_list.append(user_list[t_list[i][0]])

    print('temp_list',temp_list)
    sum_category = []
    for i in range(len(temp_list[0])):
        c = 0
        for j in range(len(temp_list)):
            c = c + temp_list[j][i]
        sum_category.append(c)
    # print(sum_category)

    user_list[user_id]=sum_category
    # user_list[499]=sum_category
    # print(user_list[499])

    major_similarity = maxuser(user_id, user_list, vol_list, vol_latlng)
    # major_similarity = maxuser(499, user_list, vol_list, vol_latlng)
    # print('major_similarity',major_similarity)
    print('major',major_similarity)

    for i in range(len(major_similarity)):
        total_list.append(major_similarity[i])

    conn.close()

    # print('=======')
    # print(total_list)
    # print('=======')
#    print('similar',similar_list)
    """ 좋아요 부분 """
    # 어느 카테고리 인지 categ
    # contents마다 user가 좋아요를 눌러놓은 게시물인지 아닌지 확인
    similar_star_rate = []
    category_names = []
    likes_bool = []
    for i in range(len(total_list)):

        likes_bool.append(already_liked(user_id,total_list[i][0]))
        category_names.append(max_classification(vol_list[total_list[i][0]]))
#         cur.execute("select * from volunteer where id=" + str(total_list[i][0]))
#         row = cur.fetchone()
# #        print(row)
# #         print('here',max_classification(row[8:-5]))
#         category_names.append(max_classification(row[8:-5]))
    """modified to sqlalchemy"""

    voluntemp = Volunteer.query.all()
    for j in range(len(voluntemp)):
        # print("voluntemp[i]는", voluntemp[j].id )
        # print("similar_list[i][1]는", similar_list[i][1])
        if voluntemp[j].id == total_list[i][0]: #similar_list[i][1]:
            row = voluntemp[j].to_tuple()
#    category_names.append(max_classification(row[8:-5]))

    for i in range(len(similar_list)):
        similar_star_rate.append(similar_star(similar_list[i][3]))

    # print('star',similar_star_rate)
    # print('vol_content22',vol_content)
    # print('star', similar_star_rate)
    return render_template('base_map.html', category_name=category_names, check_flag=likes_bool,
                                                    vol_content=vol_content, similar_list = similar_list, star_rate=similar_star_rate,
                                                    test_lng=vol_latlng,total_list=total_list,user_major=user_major,
                                                    first_city=first_city_list, city_name=first_city)
# test_lng=vol_latlng,vol_content=vol_content,
#                            similar_list=similar_list, total_list=total_list,user_major=user_major,
#                            first_city=first_city_list, city_name=first_city)


# user가 해당 게시물을 좋아요 누르면 db에 update (likes table)
@app.route('/likes_update', methods=['GET','POST'])
def update_likes():
#    user_id = 5
    user_id = current_user.get_id()
    if not user_id:
        user_id = 0 #default
#    content_id = 7 # content_id도 받아와야함!

    # conn2 = sqlite3.connect('bongsa.db')
    # cur2 = conn2.cursor()

    data = request.form['like_checked']
    content_id = request.form['content_id']
    likes= Like()

    #####
    tempUser = User_category.query.all()
    for i in range(len(tempUser)):
        if tempUser[i].id == int(user_id):
            aa = list(tempUser[i].to_tuple()[1:])
            print("User_Category", tempUser[i].to_tuple()[1:], len(tempUser[i].to_tuple()[1:]))
            print(aa)

    tempVolun = Volunteer.query.all()
    for i in range(len(tempVolun)):
        if tempVolun[i].id == int(content_id):
            bb = list(tempVolun[i].to_tuple()[8:-5])
            print("Volun_Category", tempVolun[i].to_tuple()[8:-5], len(tempVolun[i].to_tuple()[8:-5]))
            print(bb)

    sum_list = []
    subtract_list = []

    if data == 'true':  # db에 등록
        likes.user_id = user_id
        likes.content_id = content_id
        db.session.add(likes)

        #####sum#####
        for i in range(len(aa)):
            c = aa[i] + float(bb[i])
            sum_list.append(c)

        tempUser[int(user_id)].category_life = sum_list[0]
        tempUser[int(user_id)].category_world = sum_list[1]
        tempUser[int(user_id)].category_environment = sum_list[2]
        tempUser[int(user_id)].category_human = sum_list[3]
        tempUser[int(user_id)].category_disaster = sum_list[4]
        tempUser[int(user_id)].category_country = sum_list[5]
        tempUser[int(user_id)].category_home = sum_list[6]
        tempUser[int(user_id)].category_medic = sum_list[7]
        tempUser[int(user_id)].category_education = sum_list[8]
        tempUser[int(user_id)].category_administration = sum_list[9]
        tempUser[int(user_id)].category_consulting = sum_list[10]
        tempUser[int(user_id)].category_culture = sum_list[11]
        tempUser[int(user_id)].category_physical = sum_list[12]
        tempUser[int(user_id)].category_history = sum_list[13]
        tempUser[int(user_id)].category_circles = sum_list[14]
        tempUser[int(user_id)].category_travel = sum_list[15]
        tempUser[int(user_id)].category_marketing = sum_list[16]
        tempUser[int(user_id)].category_social = sum_list[17]
        tempUser[int(user_id)].category_plan = sum_list[18]
        tempUser[int(user_id)].category_language = sum_list[19]
        tempUser[int(user_id)].category_scene = sum_list[20]
        tempUser[int(user_id)].category_etc = sum_list[21]
        tempUser[int(user_id)].recruit_disabled = sum_list[22]
        tempUser[int(user_id)].recruit_oldman = sum_list[23]
        tempUser[int(user_id)].recruit_foreigner = sum_list[24]
        tempUser[int(user_id)].recruit_homeless = sum_list[25]
        tempUser[int(user_id)].recruit_multiculture = sum_list[26]
        tempUser[int(user_id)].recruit_worker = sum_list[27]
        tempUser[int(user_id)].recruit_baby = sum_list[28]
        tempUser[int(user_id)].recruit_women = sum_list[29]
        tempUser[int(user_id)].recruit_zzokbang = sum_list[30]
        tempUser[int(user_id)].recruit_teenager = sum_list[31]
        tempUser[int(user_id)].recruit_nation = sum_list[32]

    elif data == 'false':  # db에서 빼기
        temp_like = Like.query.all()
        for i in range(len(temp_like)):

            # temp_like[i].user_id는 int, current_user.get_id()--u_id는 str이다. 따라서 형변환을 해줘야함.

            if temp_like[i].user_id == int(user_id) and temp_like[i].content_id == int(request.form['content_id']):
                print(user_id)
                print(content_id)
                db.session.delete(temp_like[i])

        for i in range(len(aa)):
            c = aa[i] - float(bb[i])
            subtract_list.append(c)

        tempUser[int(user_id)].category_life = subtract_list[0]
        tempUser[int(user_id)].category_world = subtract_list[1]
        tempUser[int(user_id)].category_environment = subtract_list[2]
        tempUser[int(user_id)].category_human = subtract_list[3]
        tempUser[int(user_id)].category_disaster = subtract_list[4]
        tempUser[int(user_id)].category_country = subtract_list[5]
        tempUser[int(user_id)].category_home = subtract_list[6]
        tempUser[int(user_id)].category_medic = subtract_list[7]
        tempUser[int(user_id)].category_education = subtract_list[8]
        tempUser[int(user_id)].category_administration = subtract_list[9]
        tempUser[int(user_id)].category_consulting = subtract_list[10]
        tempUser[int(user_id)].category_culture = subtract_list[11]
        tempUser[int(user_id)].category_physical = subtract_list[12]
        tempUser[int(user_id)].category_history = subtract_list[13]
        tempUser[int(user_id)].category_circles = subtract_list[14]
        tempUser[int(user_id)].category_travel = subtract_list[15]
        tempUser[int(user_id)].category_marketing = subtract_list[16]
        tempUser[int(user_id)].category_social = subtract_list[17]
        tempUser[int(user_id)].category_plan = subtract_list[18]
        tempUser[int(user_id)].category_language = subtract_list[19]
        tempUser[int(user_id)].category_scene = subtract_list[20]
        tempUser[int(user_id)].category_etc = subtract_list[21]
        tempUser[int(user_id)].recruit_disabled = subtract_list[22]
        tempUser[int(user_id)].recruit_oldman = subtract_list[23]
        tempUser[int(user_id)].recruit_foreigner = subtract_list[24]
        tempUser[int(user_id)].recruit_homeless = subtract_list[25]
        tempUser[int(user_id)].recruit_multiculture = subtract_list[26]
        tempUser[int(user_id)].recruit_worker = subtract_list[27]
        tempUser[int(user_id)].recruit_baby = subtract_list[28]
        tempUser[int(user_id)].recruit_women = subtract_list[29]
        tempUser[int(user_id)].recruit_zzokbang = subtract_list[30]
        tempUser[int(user_id)].recruit_teenager = subtract_list[31]
        tempUser[int(user_id)].recruit_nation = subtract_list[32]

    db.session.commit()
#        execute_stm = "DELETE FROM likes WHERE user_id="+str(user_id)+" and content_id="+str(content_id)
    #     cur2.execute(execute_stm)
    #     conn2.commit()
    #
    # conn2.close()           # db 연결 해제

    if len(data) != 0:   # db에 없을 때 javascript에 전달할 말
        return json.dumps({'status':'OK'})
    else:                # db에 있을 때 javascript에 전달할 말
        return json.dumps({"status":'error'})


# content 상세 게시판
@app.route('/contents/<content_id>', methods=['GET','POST'])
def blog_detail(content_id):
    # db 연결
    user_id = current_user.get_id()
    if not user_id:
        user_id = 0 #default

    # conn = sqlite3.connect('bongsa.db')
    # cur = conn.cursor()

    # query
    # cur.execute("select * from volunteer where id="+content_id) # content_id에 해당하는 컨텐츠 가져오기
    #
    # # data fetch
    # row = cur.fetchone()

    # 봉사 컨텐츠 중 volun_id와 일치하는 컨텐츠 가져오기
    volun = Volunteer.query.all()
    row = ()
    for i in range(len(volun)):
        if volun[i].id == int(content_id):
            # data fetch
            row = volun[i].to_tuple()

    category_names, category_receivers, category_tags = classification(row[8:-5])  # 함수에 필요한 값만 보냄

    # 봉사대상, 봉사분류
    if len(category_receivers) == 0:
        category_receivers = '전체시민'
    if len(category_names) == 0:
        category_names = ''


    recruit_date = row[5][4:6]+'/'+row[5][6:8]+'/'+row[5][:4]

    # if session.user.id , session.content.id가 일치하는 데이터가 db에 있으면, likes에 미리 checked!
    # + 좋아요 표시를 누르면 db에 toggle 적용 -> 있으면 빼주고, 없으면 넣어주고!

#    user_id = 3 # example (change later)

    # 처음화면에서 좋아요가 되어있는지 아닌지 나타내기 위함
    likes_bool = already_liked(user_id, content_id)


    # execute_stm = "select count(*) from " + str(content_id)
    # cur.execute(execute_stm)
    # like_counts = cur.fetchone()
    #
    # conn.close()

    likequery = Like.query.all()
    like_counts = 0
    for i in range(len(likequery)):
        if likequery[i].content_id == int(content_id):
            # data fetch
            like_counts += 1

    return render_template('blog-detail.html', contents=row, category_receiver = category_receivers,
                           category_name = category_names, tags =category_tags, recruit_date = recruit_date,
                           check_flag=likes_bool, like_counts=like_counts)


# tag 누르면 카테고리별로 봉사활동 보여주는 페이지 구현...? 할지 안할지
@app.route('/<tag_num>')
def get_tag_content(tag_num):
    category_dict = {0: '생활편의', 1: '국제협력', 2: '환경', 3: '인권', 4: '재해/재난', 5: '농어촌', 6: '주거환경', 7: '보건의료',
                     8: '교육', 9: '행정지원', 10: '상담', 11: '문화', 12: '체육', 13: '역사', 14: '동아리', 15: '여행', 16: '홍보',
                     17: '사회공헌', 18: '기획', 19: '언어', 20: '현장', 21: '기타'}
    receiver_dict = {0: '장애인', 1: '노인', 2: '외국인', 3: '노숙인', 4: '다문화가정', 5: '노동자', 6: '유아', 7: '여성', 8: '쪽방촌', 9: '청소년',
                     10: '지역사회'}
    #tag_num+8?

    # key_value 쌍으로 해야 될듯
    # key는 한글 , value는 column number(숫자로) -> jsp에 전달

    return render_template('listing-row.html')


@app.route('/more/<name>')
def more_page(name=None):
    global more_recommend, vol_content, t_list, first_city_list, first_city, category_names, likes_bool, more_categories, major_similarity
    if name == 'recommend':
        similar_star_rate_ = []
        for i in range(len(more_recommend)):
            similar_star_rate_.append(similar_star(more_recommend[i][3]))
        # print('more_rec',more_recommend)



        return render_template('more_recommend.html', vol_content=vol_content, category_name=more_categories, check_flag=likes_bool,star_rate=similar_star_rate_,
                           name= name, similarity = more_recommend)
    elif name == 'nation':
        city_categories = []
        for i in range(len(first_city_list)):
            city_categories.append(max_classification(vol_list[first_city_list[i][0]]))
        return render_template('more_nation.html', vol_content=vol_content,category_name=city_categories, check_flag=likes_bool,
                               name=name, city_name = first_city,city=first_city_list)
    elif name == 'major':
        print('mj',major_similarity)
        similar_star_rate_ = []
        for i in range(len(major_similarity)):
            similar_star_rate_.append(similar_star(major_similarity[i][3]))
        major_len = len(t_list)


        major_categories = []
        for i in range(len(major_similarity)):
            major_categories.append(max_classification(vol_list[major_similarity[i][0]]))
        return render_template('more_major.html', vol_content=vol_content,category_name=major_categories, check_flag=likes_bool,star_rate=similar_star_rate_,
                               name=name, major_len=major_len,
                               major_list=major_similarity, city=first_city_list)

if __name__ == '__main__':
    app.run()
