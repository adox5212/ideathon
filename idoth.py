from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://route=/database/structure&db=clientalgeria'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model (Consolidated)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Role: Client, Freelancer, etc.
    coins = db.Column(db.Integer, default=0)  # Default coins to 0
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Referrer ID

# Homepage Route
@app.route('/')
def home():
    return render_template('ideatho.html')

@app.route('/explore')
def explore():
    return "Explore Page"

# Route for becoming a seller
@app.route('/become-seller', methods=['GET', 'POST'])
def become_seller():
    if request.method == 'POST':
        # Retrieve form data
        print(request.form)  # Print all the form data for debugging
        username = request.form.get('username')  
        email = request.form.get('email')
        phone = request.form.get('phone', None)
        location = request.form.get('location', 'Algeria')  # Default location
        role = request.form.get('role', 'Client')  # Default role if not specified
        password = request.form.get('password')  # Use get() to avoid KeyError

        # Check if password is provided
        if not password:
            return render_template('aftersignin.html')  # Respond with an error message

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Save user to the database
        new_user = User(username=username, email=email, phone=phone, location=location, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

    return render_template('becaumeseller.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        referrer_id = request.form.get('referrer_id')  # Optional referral code

        # Validate and create user
        if not password:
            return render_template('aftersignin.html')
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        # Handle referral
        if referrer_id:
            referrer = User.query.get(referrer_id)
            if referrer:
                new_user.referred_by = referrer.id
                referrer.coins += 50  # Award 50 coins for a successful referral
                db.session.add(referrer)

        db.session.add(new_user)
        db.session.commit()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        print(request.form)  # Print all the form data for debugging
        username = request.form.get('username') 
        password = request.form.get('password')  # Use get() to avoid KeyError

        # Check if password is provided
        if not password:
            return render_template('aftersignin.html')  # Respond with an error message

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Save user to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

    return render_template('login.html')

# Payment Route
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Process payment details (placeholder for now)
        return "Payment successful! Thank you."

    return render_template('payment.html')

@app.route('/earn-coins', methods=['POST'])
def earn_coins():
    user_id = request.form.get('user_id')  # Assume user_id is passed in the form
    activity = request.form.get('activity')  # Type of activity

    # Define coins earned for each activity
    coin_rewards = {
        'referral': 50,  # Earn 50 coins for referrals
        'workshop': 20,  # Earn 20 coins for attending workshops
        'service': 10    # Earn 10 coins for using services
    }

    if activity not in coin_rewards:
        return {"message": "Invalid activity type"}, 400

    # Find the user in the database
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    # Update user's coins
    user.coins += coin_rewards[activity]
    db.session.commit()

    return {"message": f"{coin_rewards[activity]} coins added. Total coins: {user.coins}"}, 200

@app.route('/workshop-attend', methods=['POST'])
def workshop_attend():
    user_id = request.form.get('user_id')  # User attending workshop
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found"}, 404

    user.coins += 20  # Add 20 coins for workshop attendance
    db.session.commit()
    return {"message": "20 coins added for workshop attendance!"}, 200

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
