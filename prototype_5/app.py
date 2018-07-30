from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testuser.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.update({'SECRET_KEY':'윤성찬'})

db = SQLAlchemy(app)
admin = Admin(app)


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.String, primary_key=True)
    pwd = db.Column(db.String, nullable=False)


@app.route('/')
def main_screens():
    return render_template('main_screen.html')


@app.route('/login/')
def hello_logins():
    return render_template('login_2.html')


@app.route('/test', methods=['POST'])
def hello_world_id():
    login_id = request.form['login']
    login_pwd = request.form['password']
    user = User()
    user.id = login_id
    user.pwd = login_pwd
    db.session.add(user)
    db.session.commit()
    return render_template('test.html',id=login_id,pwd=login_pwd)


if __name__ == '__main__':
    app.run()
