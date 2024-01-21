from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
USERS_FILE = 'users.json'
CARS_FILE = 'cars.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return []

def save_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_users():
    return load_data(USERS_FILE)

def save_users(users_data):
    save_data(users_data, USERS_FILE)

def load_cars():
    return load_data(CARS_FILE)

def save_cars(cars_data):
    try:
        with open(CARS_FILE, 'w') as file:
            json.dump(cars_data, file, indent=4)
            print('Cars data saved successfully.')
    except Exception as e:
        print(f'Error saving cars data: {e}')

users = load_users()
cars = load_cars()

@app.context_processor
def inject_variables():
    return dict(os=os)

@app.route('/')
def home():
    cars = load_cars()
    return render_template('home.html', cars=cars)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            users[username] = {'password': password}
            save_users(users)
            flash('Signup successful!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            flash('Login successful!', 'success')
            return redirect(url_for('post_car'))

        flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/post_car', methods=['GET', 'POST'])
def post_car():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        price = request.form['price']
        contact_info = request.form['contact_info']
        filename = None  # Initialize filename

        if 'photo' in request.files:
            file = request.files['photo']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'error')

        car_data = {'make': make, 'model': model, 'price': price, 'contact_info': contact_info, 'photo': filename}
        cars.append(car_data)

        save_cars(cars)  # Save the cars data

        flash('Car posted successfully!', 'success')
        return redirect(url_for('view_cars'))

    return render_template('post_car.html', cars=cars)


@app.route('/view_cars')
def view_cars():
    cars = load_cars()
    return render_template('view_cars.html', cars=cars)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True, host='0.0.0.0')
