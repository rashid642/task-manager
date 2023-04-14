from flask import Flask,render_template,request,redirect,flash,session,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/?'
db = SQLAlchemy(app)

IST = pytz.timezone('Asia/Kolkata')

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    user_name = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    password = db.Column(db.String(60),nullable = False)

    def __repr__(self):
        return f"{self.user_name}"

class UserSession(db.Model):
    session_id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(120), nullable = False)
    set_date = db.Column(db.DateTime, default = datetime.now(IST))

class Task(db.Model):
    sno = db.Column(db.Integer,primary_key = True)
    task = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.now(IST))
    completed = db.Column(db.Integer,default = 0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    user = db.relationship('User',backref=db.backref('task', lazy=True))
    
    def __repr__(self):
        return f"{self.task}"

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            user_id = User.query.filter_by(email = user_email).first().id
            task = request.form['task']
            desc = request.form['desc']
            todo = Task(task = task,desc = desc,user_id = user_id)
            db.session.add(todo)
            db.session.commit()
            print(todo.task)
            message = "Task Added Successfully!!"
            flash(message)
            return redirect(url_for('home'))   
        else:
            message = "Please Login!!"
            flash(message)
            return redirect(url_for('login'))     
    else:
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            user_id = User.query.filter_by(email = user_email).first().id
            alltodo = Task.query.filter_by(user_id = user_id).all()
            return render_template('home.html', alltodo = alltodo)
        else:
            return render_template('home.html')

@app.route('/delete/<int:sno>')
def delete(sno):
    if 'user' in session:
        user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
        user_id = User.query.filter_by(email = user_email).first().id
        check_sno = Task.query.filter_by(sno = sno).first()
        if check_sno != None:
            check_user_id = check_sno.user_id
            if check_user_id == user_id:
                db.session.delete(check_sno)
                db.session.commit()
                message = "Task deleted Successfully"
                flash(message)
                return redirect(url_for('home'))
            else:
                message = "This Task doesn't exist"
                flash(message)
                return redirect(url_for('home'))
        else:
            message = "This Task doesn't exist"
            flash(message)
            return redirect(url_for("home"))
    else:
        message = "Please Login"
        flash(message)
        return redirect(url_for("login"))

@app.route('/update/<int:sno>',methods = ['GET','POST'])
def update(sno):
    if request.method == 'POST':
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            user_id = User.query.filter_by(email = user_email).first().id
            check_sno = Task.query.filter_by(sno = sno).first()
            if check_sno != None:
                check_user_id = check_sno.user_id
                if check_user_id == user_id:
                    task = request.form['task']
                    desc = request.form['desc']
                    check_sno.task = task
                    check_sno.desc = desc
                    db.session.add(check_sno)
                    db.session.commit()
                    message = "Task Updated!!"
                    flash(message)
                    return redirect(url_for('home'))
                else:
                    message = "This Task doesn't exist"
                    flash(message)
                    return redirect(url_for('home'))
            else:
                message = "This Task doesn't exist"
                flash(message)
                return redirect(url_for('home'))
        else:
            message = "Please Login"
            flash(message)
            return redirect(url_for("login"))
    else:
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            user_id = User.query.filter_by(email = user_email).first().id
            check_sno = Task.query.filter_by(sno = sno).first()
            if check_sno != None:
                check_user_id = check_sno.user_id
                if check_user_id == user_id:
                    return render_template('update.html',todo = check_sno)
                else:
                    message = "This Task doesn't exist"
                    flash(message)
                    return redirect(url_for('home'))
            else:
                    message = "This Task doesn't exist"
                    flash(message)
                    return redirect(url_for('home'))
        else:
            message = "Please Login"
            flash(message)
            return redirect(url_for("login"))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            if email != "" and password != "":
                existing_user = User.query.filter_by(email = email).first()
                if existing_user == None:
                    user = User(user_name = user_name,email = email,password = password)
                    db.session.add(user)
                    db.session.commit()
                    message = "Account Created Successfully!" 
                    # status = "success"
                    flash(message)
                    return redirect(url_for('login')) 
                else:
                    message = "Account already exists."
                    flash(message)
                    return redirect(url_for('register'))           
            else:
                message = "Please enter email and password!!"
                flash(message)
                return redirect(url_for('register'))       
        else:
            message = "Password didn't match" 
            flash(message)
            return redirect(url_for('register'))          
    else:
        return render_template('register.html')

@app.route('/login',methods =['POST','GET'])
def login():
    if request.method == 'POST':
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            message = f"{user_email} is already logged in."
            flash(message)
            return redirect(url_for('home'))
        else:
            user_email = request.form['email']
            password = request.form['password']
            if user_email != "" and password != "":
                email = User.query.filter_by(email = user_email).first()
                if email != None:
                    check_password = email.password
                    if password == check_password:
                        new_session = UserSession(email = user_email,set_date = datetime.now())
                        db.session.add(new_session)
                        db.session.commit()
                        session["user"] = new_session.session_id
                        message = "Logged In Successfully"
                        flash(message)
                        return redirect(url_for('home'))
                    else:
                        message = "Wrong password!!\nPlease Enter correct Password."
                        flash(message)
                        return redirect(url_for('login'))
                else:
                    message = "No such User found. Please register!!"
                    flash(message)
                    return redirect(url_for('register'))
            else:
                message = "Please enter email and password!!"
                flash(message)
                return redirect(url_for('login')) 
    else:
        if 'user' in session:
            user_email = UserSession.query.filter_by(session_id = session["user"]).first().email
            message = f"{user_email} is already logged in."
            flash(message)
            return redirect(url_for('home'))
        else:
            return render_template('login.html')

@app.route('/logout',methods =['GET'])
def logout():
    if 'user' in session:
        current_session = UserSession.query.filter_by(session_id = session['user']).first()
        db.session.delete(current_session)
        db.session.commit()
        session.pop('user')
        message = "User logged out Successfully."
        flash(message)
        return redirect(url_for('home'))
    else:
        message = "User is already logged out."
        flash(message)
        return redirect(url_for('login'))


@app.route('/contact',methods = ['GET','POST'])
def contact():
    return render_template('contact.html')
    
@app.before_first_request
def create_tables():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)