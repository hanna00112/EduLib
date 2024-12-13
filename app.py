from flask import Flask, redirect, render_template, request, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os, re
from datetime import datetime
import requests


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
                    return jsonify({"message": "Welcome Admin!", "redirect": url_for('Admin_home')}), 200
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


@app.route('/myaccount')
def home():
    books = Book.query.all()
    return render_template('non-admin/student-home.html', books=books)

# to access the admin home page
@app.route('/admin/home')
def Admin_home():
    books = Book.query.all()
    return render_template('admin/admin-home.html', books=books)


# INDEX Page -- login
@app.route('/index')
def main():
    return render_template('index.html')

@app.route('/api/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()  
    return jsonify([role.name for role in roles])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
          # Handle submission from user
        if request.is_json:
            data = request.json
            # Get form data
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password = data.get('password')
            roles = data.get('roles', [])
        else:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            roles = request.form.getlist('roles')
        # Normalize roles to a list
        if isinstance(roles, str):  # If it's a single role wrap it in a list
            roles = [roles]

        print("Received data:", roles)
        # Validate input
        if not first_name or not last_name or not email or not password or not roles:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('register'))

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format"}), 400
        
        #valid role combinations
        valid_combinations = [
            {"admin"},                    # Admin alone
            {"admin", "faculty"},         # Admin and Faculty
            {"faculty"},                  # Faculty alone
            {"student"},                  # Student alone
            {"student", "admin"}          # Student and Admin
        ]

        # Convert user input into a set for easy comparison
        user_roles_set = set(roles)

        # Check if the provided roles match one of the valid combinations
        
        if user_roles_set not in valid_combinations:
           flash('Invalid role combination', 'error')
           return redirect(url_for('register'))
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create new user and hash the password
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email

        )
        new_user.set_password(password)  # Hash the password

         # Add roles to the user
        db_roles = Role.query.filter(Role.name.in_(roles)).all()
        for role in db_roles:
            new_user.roles.append(role)
        

        # Add to the database
        db.session.add(new_user)
        print("Committing to the database...")
        db.session.commit()
        print("Commit successful.")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # If GET request, render the registration form
    return render_template('signup.html')

#@app.route('/nait')
#def mohammed():
   # return render_template('admin/admin-add.html')




#////////////////////////////////////////////////////////////////////////////////////
# For the bot in order to work, the hosting computet should gpt4all installed as well as one of llama 3 models :3
def search_books(query):
    """
    Search for books in the database based on title, author, or ISBN
    """
    try:
        # Convert query to lowercase for case-insensitive search
        query = query.lower()
        
        # Search in database using SQLAlchemy
        books = Book.query.filter(
            db.or_(
                db.func.lower(Book.title).contains(query),
                db.func.lower(Book.author).contains(query),
                Book.isbn.contains(query)
            )
        ).all()
        
        # Format results
        results = []
        for book in books:
            results.append({
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'status': book.copy_status,
                'location': book.location
            })
        
        return results
    except Exception as e:
        return f"Error searching books: {str(e)}"

def gpt4all_response(conversation_history):
    """
    Send a request to GPT4All API and return the response.
    """
    API_URL = "http://localhost:4891/v1/chat/completions"
    payload = {
        "messages": conversation_history,
        "model": "gpt4all-j",
        "temperature": 0.7,
        "max_tokens": 2000  # Adjust based on your needs
    }
    
    try:
        # Make the API request
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            # Return the chatbot's response
            return response.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to GPT4All API"


#/////////////////////////////////////////////////////////////////////////////////////



@app.route('/chatbot', methods=['POST'])

def chat_with_library_assistant():
    """
    Handle chatbot requests from JavaScript frontend
    """
    try:
        # Get the message from the JSON request
        data = request.get_json()
        user_input = data.get('message', '').strip()

        # System prompt for the assistant
        system_prompt = {
            "role": "system", 
            "content": """You are a helpful library management assistant, you have to act as your own library, do not referr the user to any other external resource other than Al akhawayn university library, if someone asks for a book look up if it is in Al Akhawayn university library, You can help with:
            - Book searches and recommendations
            - Library membership information
            - Check-out and return procedures
            - Library policies and rules
            - Finding resources by category or subject
            - Library hours and services
            - Study room reservations
            - Library events and programs
            Please provide clear, accurate information about library services and resources."""
        }

        # Initialize conversation history
        conversation_history = [system_prompt]

        # Check if it's a book search query
        if any(keyword in user_input.lower() for keyword in ['find book', 'search book', 'looking for book']):
            # Extract search query
            search_terms = user_input.lower().replace('find book', '').replace('search book', '').replace('looking for book', '').strip()
            
            # Search for books
            results = search_books(search_terms)
            
            if isinstance(results, list) and results:
                response = "I found the following books:\n"
                for book in results:
                    response += f"\nTitle: {book['title']}\n"
                    response += f"Author: {book['author']}\n"
                    response += f"ISBN: {book['isbn']}\n"
                    response += f"Status: {book['status']}\n"
                    response += f"Location: {book['location']}\n"
                    response += "-" * 40 + "\n"
            elif isinstance(results, list):
                response = "I couldn't find any books matching your search criteria."
            else:
                response = results  # This would be the error message
        else:
            # Use GPT4All for non-database-related queries
            conversation_history.append({"role": "user", "content": user_input})
            response = gpt4all_response(conversation_history)

        return jsonify({
            "response": response,
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "response": f"An error occurred: {str(e)}",
            "status": "error"
        }), 500

#/////////////////////////////////////////////////////////////////////////////////////

if __name__ == '__main__':
    app.run(debug=True, port=5001)
