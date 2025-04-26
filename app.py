from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import os
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

bcrypt = Bcrypt(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['fitness_db']
users = db['users']
bmi_records = db['bmi_records']
# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    user_data = users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'logout', 'static']  
    if not current_user.is_authenticated and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/workouts')
@login_required
def workouts():
    return render_template('workouts.html')

@app.route('/nutrition')
@login_required
def nutrition():
    return render_template('nutrition.html')

@app.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi():
    bmi_records = list(db.bmi_records.find({'user_id': current_user.id}).sort("date", -1))

    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height']) / 100
        bmi = round(weight / (height ** 2), 1)

        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        db.bmi_records.insert_one({
            "user_id": current_user.id,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category,
            "date": datetime.utcnow()
        })

        bmi_records = list(db.bmi_records.find({'user_id': current_user.id}).sort("date", -1))
        return render_template('bmi.html', bmi=bmi, category=category, bmi_records=bmi_records)

    return render_template('bmi.html', bmi_records=bmi_records)

@app.route('/delete_bmi/<record_id>', methods=['POST'])
@login_required
def delete_bmi(record_id):
    db.bmi_records.delete_one({"_id": ObjectId(record_id), "user_id": current_user.id})
    flash("BMI record deleted successfully!", "success")
    return redirect(url_for('bmi'))

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        return redirect(url_for('contact_success', name=name))
    return render_template('contact.html')

@app.route('/contact/success')
@login_required
def contact_success():
    name = request.args.get('name', 'there')
    return render_template('contact_success.html', name=name)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = users.find_one({'$or': [{'username': username}, {'email': email}]})
        
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_id = users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        }).inserted_id
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = users.find_one({'username': username})
        
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    result = users.delete_one({'_id': ObjectId(current_user.id)})

    if result.deleted_count:
        logout_user() 
        flash('Your account has been deleted successfully.', 'success')
    else:
        flash('Account deletion failed. Please try again.', 'danger')

    return redirect(url_for('signup'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)

if __name__ == '__main__':
    app.run(debug=True)
