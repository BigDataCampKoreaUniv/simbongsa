from flask import Flask, render_template, request, redirect, url_for, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_security.forms import RegisterForm
from flask_security.views import _ctx, register_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user

from get_coordinates import GeoCoordinates

app = Flask(__name__)

# Database 생성
app.config['DEBUG'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = '심봉사'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECRET_KEY'] = '심봉사'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
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
    for i in range(1,21):
        locals()[f"volun{i}"] = db.Column(db.Integer())
    prefer_bloc1 = db.Column(db.String(255))
    prefer_sloc1 = db.Column(db.String(255))
    prefer_bloc2 = db.Column(db.String(255))
    prefer_sloc2 = db.Column(db.String(255))
    prefer_bloc3 = db.Column(db.String(255))
    prefer_sloc3 = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore) # Security 기능 확장 위함





#@app.before_first_request # 초기화할때
def create_user():
    db.create_all()
    user_datastore.create_user(email='sungje5957@gmail.com', password='pw')
    db.session.commit()


@app.route('/')
def index():
    get_add = GeoCoordinates('서울 중구 덕수궁길 15')
    print(get_add['result']['items'][0]['point']['x'], get_add['result']['items'][0]['point']['y'])
    return render_template('base.html')


# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)


@app.route('/googlemap')
def googlemap():
    return render_template('googlemap.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('login.html')


@app.route('/register/search', methods=['GET', 'POST'])
def searchuniv():
    import pandas as pd
    univ_data = pd.read_csv(r'static\\대학현황.csv', engine='python',
                       encoding='utf-8-sig')
    univNameMajor = univ_data[['학교명', '학부·과(전공)명']]
    univName = pd.Series(univ_data['학교명'].unique())

    univDict={}
    univList = []
    major=[]
    if request.method == 'POST':

        if request.form['search3'] == "대학교검색":
            univ = request.form['search']
            for univ_name in univName:
                if univ in univ_name:
                    univDict[univ_name]= list(univ_data[univ_data['학교명'] == univ_name]['학부·과(전공)명'])


        # elif request.form['search3'] == '전공검색':
        #     univ2 = request.form['univ']
        #     major = list(univ_data[univ_data['학교명'] == univ2]['학부·과(전공)명'])

    return render_template("search.html", univDict=univDict)


@app.route('/register/', methods=['GET','POST'])
# @anonymous_user_required
def register_users():

    register_user_form = RegisterForm()

    if request.method == 'POST':
        if register_user_form.validate_on_submit():
            user = register_user(**register_user_form.to_dict())
            user.sex = request.form['mf']
            user.grade = request.form['grade']
            if request.form.get('volun1', None):
                user.volun1 = 1
            else:
                user.volun1 = 0

            if request.form.get('volun2', None):
                user.volun2 = 1
            else:
                user.volun2 = 0

            if request.form.get('volun3', None):
                user.volun3 = 1
            else:
                user.volun3 = 0

            if request.form.get('volun4', None):
                user.volun4 = 1
            else:
                user.volun4 = 0

            if request.form.get('volun5', None):
                user.volun5 = 1
            else:
                user.volun5 = 0

            if request.form.get('volun6', None):
                user.volun6 = 1
            else:
                user.volun6 = 0

            if request.form.get('volun7', None):
                user.volun7 = 1
            else:
                user.volun7 = 0

            if request.form.get('volun8', None):
                user.volun8 = 1
            else:
                user.volun8 = 0

            if request.form.get('volun9', None):
                user.volun9 = 1
            else:
                user.volun9 = 0

            if request.form.get('volun10', None):
                user.volun10 = 1
            else:
                user.volun10 = 0
            if request.form.get('volun11', None):
                user.volun11 = 1
            else:
                user.volun11 = 0
            if request.form.get('volun12', None):
                user.volun12 = 1
            else:
                user.volun12 = 0
            if request.form.get('volun13', None):
                user.volun13 = 1
            else:
                user.volun13 = 0
            if request.form.get('volun14', None):
                user.volun14 = 1
            else:
                user.volun14 = 0
            if request.form.get('volun15', None):
                user.volun15 = 1
            else:
                user.volun15= 0
            if request.form.get('volun16', None):
                user.volun16 = 1
            else:
                user.volun16 = 0
            if request.form.get('volun17', None):
                user.volun17 = 1
            else:
                user.volun17 = 0
            if request.form.get('volun18', None):
                user.volun18 = 1
            else:
                user.volun18 = 0
            if request.form.get('volun19', None):
                user.volun19 = 1
            else:
                user.volun19 = 0
            if request.form.get('volun20', None):
                user.volun20 = 1
            else:
                user.volun20 = 0

            user.prefer_bloc1 = request.form['category']
            user.prefer_sloc1 = request.form['choices']
            user.prefer_bloc2 = request.form['category1']
            user.prefer_sloc2 = request.form['choices1']
            user.prefer_bloc3 = request.form['category2']
            user.prefer_sloc3 = request.form['choices2']

            register_user_form.user = user
            db.session.commit()
            return redirect(url_for('index')) # register가 완성되면 초기페이지로
        else:
            flash(register_user_form.errors, 'info')
            return render_template("register.html", register_user_form=register_user_form, **_ctx('register'))
    else:
        return render_template("register.html", register_user_form=register_user_form)



if __name__ == '__main__':
    app.run()
