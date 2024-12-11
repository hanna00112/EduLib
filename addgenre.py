from app import app, db
from app import Genre

# Add genres to the table
genres = ['Fantasy', 'Science Fiction', 'Non-Fiction', 'Biography', 'Mystery', 'Horror', 'Computer Science', 'History']

# Run within the Flask application context
with app.app_context():
    for genre_name in genres:
        # Check if the genre already exists to avoid duplicates
        if not Genre.query.filter_by(name=genre_name).first():
            new_genre = Genre(name=genre_name)
            db.session.add(new_genre)

    db.session.commit()
    print("Genres added successfully!")