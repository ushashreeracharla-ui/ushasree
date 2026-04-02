from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret"

# SQLite Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databasedb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ MYSQL CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:harsha@localhost/databasedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection failed:", e)


# ================= MODELS =================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    profile_pic = db.Column(db.String(100), default='default.png')
    streak = db.Column(db.Integer, default=0)
    last_completed = db.Column(db.Date)

    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete")


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(255))
    deadline = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= HELPER =================


def get_alert(deadline):
    if not deadline:
        return ""

    # ✅ FIX: convert string → date
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, "%Y-%m-%d").date()

    today = date.today()
    diff = (deadline - today).days

    if diff < 0:
        return "⚠ Overdue"
    elif diff == 0:
        return "⏰ Today"
    elif diff == 1:
        return "🔔 Tomorrow"
    elif diff <= 2:
        return "📅 Soon"
    else:
        return ""
# ================= ROUTES =================
'''@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        tasks = Task.query.filter_by(user_id=session['user_id']).all()
        return render_template("home.html", user=user, tasks=tasks)
    return render_template("home.html", user=None, tasks=[])

#@app.route('/')
#def home():
   # return render_template('home.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        user = User.query.filter_by(username=u, password=p).first()

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        new_user = User(username=u, password=p)

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')  
    '''

# LANDING PAGE (Task Mate first screen)
@app.route('/')
def landing():
    return render_template('landing.html')gyu 8










    00 


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        user = User.query.filter_by(username=u, password=p).first()

        if user:
            session['user_id'] = user.id
            #flash("Login Successful", "success")
            return redirect('/home')
        else:
            flash("Invalid Username or Password", "danger")
            return redirect('/login')
    return render_template('login.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']

        user = User.query.filter_by(username=username).first()

        if user:
            user.password = new_password
            db.session.commit()
            flash("Password updated successfully", "success")
            return redirect('/login')
        else:
            flash("User not found", "danger")

    return render_template('forgot.html')


# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        new_user = User(username=u, password=p)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

'''
# HOME PAGE (AFTER LOGIN)
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()

    return render_template('home.html', user=user, tasks=tasks)
'''

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')

    user = User.query.get(session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).all()

    alerts = [get_alert(t.deadline) for t in tasks]

    return render_template("home.html", user=user, tasks=tasks, alerts=alerts)




# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/')

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        db.session.commit()
        return redirect('/home')

    return render_template('profile.html', user=user)


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    uid = session['user_id']

    tasks = Task.query.filter_by(user_id=uid).all()
    user = User.query.get(uid)

    alerts = [get_alert(t.deadline) for t in tasks]

    return render_template('dashboard.html', tasks=tasks, alerts=alerts, user=user)
@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/')

    query = request.args.get('q')

    results = Task.query.filter(
        Task.user_id == session['user_id'],
        Task.title.ilike(f"%{query}%")
    ).all()

    user = User.query.get(session['user_id'])
    alerts = [get_alert(t.deadline) for t in results]

    return render_template("home.html", tasks=results, user=user, alerts=alerts)
# ADD TASK
# ADD TASK
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/')

    uid = session['user_id']
    title = request.form.get('title')
    description = request.form.get('description')
    ttype = request.form.get('type')
    
    # 1. GET THE DEADLINE FROM THE FORM FIRST
    deadline_raw = request.form.get('deadline')
    
    # 2. CONVERT STRING TO DATE OBJECT
    deadline_date = None
    if deadline_raw:
        try:
            deadline_date = datetime.strptime(deadline_raw, "%Y-%m-%d").date()
        except ValueError:
            deadline_date = None

    # 3. CREATE THE TASK
    new_task = Task(
        title=title,
        description=description,
        type=ttype,
        deadline=deadline_date, # Use the converted date object here
        user_id=uid
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect('/dashboard')

    # ✅ FIX: convert string → date
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, "%Y-%m-%d").date()

    today = date.today()
    diff = (deadline - today).days

    if diff < 0:
        return "⚠ Overdue"
    elif diff == 0:
        return "⏰ Today"
    elif diff == 1:
        return "🔔 Tomorrow"
    elif diff <= 2:
        return "📅 Soon"
    else:
        return ""

    new_task = Task(
        title=title,
        description=description,
        type=ttype,
        deadline=deadline,
        user_id=uid
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect('/dashboard')
# EDIT TASK
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.type = request.form['type']
        task.deadline = datetime.strptime(request.form['deadline'], "%Y-%m-%d").date()
        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit.html', task=task)


# COMPLETE TASK
@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get(id)
    task.status = 'Completed'
    db.session.commit()
    return redirect('/dashboard')


# DELETE TASK
# DELETE TASK
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/')
        
    task = Task.query.get(id)

    # Security check: Ensure the task belongs to the logged-in user
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()

    # Change this to redirect back to home
    return redirect('/home')


# CALENDAR
@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect('/')

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template('calendar.html', tasks=tasks)

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect('/')

    tasks = Task.query.filter_by(user_id=session['user_id']).all()

    notes = []
    for t in tasks:
        alert = get_alert(t.deadline)
        if alert:
            notes.append(f"{t.title} → {alert}")

    return {"notifications": notes}




@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect('/')

    user = User.query.get(session['user_id'])

    user.username = request.form['username']
    user.email = request.form['email']

    # Image upload
    file = request.files['file']
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        path = os.path.join('static/images', filename)
        file.save(path)
        user.profile_pic = filename

    db.session.commit()
    return redirect('/profile')

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # creates tables in MySQL

    app.run(debug=True)