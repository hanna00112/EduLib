from flask import Flask, redirect, render_template, request, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import re
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set secret key for sessions
app.secret_key = os.urandom(24)  # You can replace this with a fixed key for production
bcrypt = Bcrypt(app)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edulife.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask Migrate
migrate = Migrate(app, db)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    isbn = db.Column(db.String(13), nullable=False)
    location = db.Column(db.String(255))
    copy_status = db.Column(db.String(50))

    # Many-to-many relationship with Genre
    genres = db.relationship('Genre', secondary='book_genre', back_populates='books')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Many-to-many relationship with Book 
    books = db.relationship('Book', secondary='book_genre', back_populates='genres')

class BookGenre(db.Model):
    __tablename__ = 'book_genre'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), primary_key=True)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Many-to-many relationship with Role
    roles = db.relationship('Role', secondary='user_role', back_populates='users')
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# Define the Role model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Many-to-many relationship with User
    users = db.relationship('User', secondary='user_role', back_populates='roles')

# Define UserRole model for many-to-many relationship
class UserRole(db.Model):
    __tablename__ = 'user_role'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)

# Define the BookCheckoutHistory model
class BookCheckoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    late_fine = db.Column(db.Integer, nullable=False)
    # Relationships
    book = db.relationship('Book', backref='checkouts')
    user = db.relationship('User', backref='checkouts')

# Migration set up
with app.app_context():
    db.create_all()

# Function to serialize books and convert ObjectId to string
def serialize_books(book):
    book['_id'] = str(book['_id'])  # Convert ObjectId to string
    return book

@app.route('/test', methods=['GET'])
def test():
    return 'Flask is working!'

@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            # Handle submission from user
            if request.is_json:
                data = request.json
                email = data.get('email')
                password = data.get('password')
                user_type = data.get('userType')
            else:
                email = request.form.get('email')
                password = request.form.get('password')
                user_type = request.form.get('userType')

            # Validate 
            if not email or not password or not user_type:
                return jsonify({"error": "Please fill in all fields"}), 400

            # Validate user type
            if user_type == "admin":
                user_roles = ['admin']
            elif user_type == "non-admin":
                user_roles = ['faculty', 'student']
            else:
                return jsonify({"error": "Invalid user type"}), 400
            
            # Query the user by email
            user = User.query.filter_by(email=email).first()

            # Check user credentials
            if user and user.check_password(password):
                # Ensure the user has the correct role
                if user_type == "admin" and any(role.name == "admin" for role in user.roles):
                    session['user_id'] = user.id
                    session['user_role'] = 'admin'
                    return jsonify({"message": "Welcome Admin!", "redirect": url_for('add_book')}), 200
                elif user_type == "non-admin" and any(role.name in user_roles for role in user.roles):
                    session['user_id'] = user.id
                    session['user_role'] = 'non-admin'
                    return jsonify({"message": f"Welcome {user_type}!", "redirect": url_for('home')}), 200
                else:
                    return jsonify({"error": f"User does not have the {user_type} role"}), 403

            else:
                return jsonify({"error": "Invalid login credentials"}), 401
        
            # If GET request, render the login page
        return render_template('index.html')

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method =='POST':
        print("POST request received")  # Debug log
        
        data = request.json
        print(f"JSON data received: {data}")  # Debug log
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        user_types = data.get('userType',[]) #A list of user types

        
        # Normalize `user_types` to a list
        if isinstance(user_types, str):  # If it's a single role wrap it in a list
            user_types = [user_types]
        print(f"User types normalized: {user_types}")
        # Validate 
        if not email or not password or not user_types:
            return jsonify({"error": "Please fill in all fields"}), 400
        
        # Validate email format
        
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format"}), 400

        #check if email exists in database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        #check if the role exists in teh database
        valid_roles = Role.query.filter(Role.name.in_(user_types)).all()
        if len(valid_roles) != len(user_types):
            return jsonify({"error": "Invalid role(s) provided"}), 400
        
        #hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
       

       #create a new user
        new_user= User(first_name=first_name, last_name=last_name,email=email,password=hashed_password)
        
        try:
            new_user.roles=valid_roles
        
            #add and commit the user to the database
            db.session.add(new_user)
            db.session.commit()
            print("User registered successfully")  # Debug log
            return jsonify({"success": "Registration successful"}), 200
            
            return redirect(url_for('login')) #after registration, user is sent back to the login page
        
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")  # Debug log
            return jsonify({"error": f"Registration failed: {str(e)}"}), 500
        
    return render_template('sign-up.html') 






@app.route('/myaccount')
def home():
    books = Book.query.all()
    return render_template('non-admin/student-home.html', books=books)


#@app.route('/nait')
#def mohammed():
   # return render_template('admin/admin-add.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)