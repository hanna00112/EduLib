from app import db, app, User, Role  # Import necessary modules from your app

def add_user():
    """
    Adds an admin role and user to the database if they do not already exist.
    """
    with app.app_context():
        # Ensure the "admin" role exists
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin")
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created.")
        else:
            print("Admin role already exists.")

        # Add an admin user
        admin_email = "admin@aui.ma"  # Admin email
        existing_user = User.query.filter_by(email=admin_email).first()

        if not existing_user:
            admin_user = User(
                first_name="Admin",
                last_name="User",
                email=admin_email
            )
            admin_user.set_password("adminpassword")  # Replace with a secure password
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user with email '{admin_email}' added successfully.")
        else:
            print(f"Admin user with email '{admin_email}' already exists.")

        # Add a faculty user
        faculty_email = "faculty@aui.ma"  # Faculty email
        existing_faculty_user = User.query.filter_by(email=faculty_email).first()

        if not existing_faculty_user:
            faculty_user = User(
                first_name="Faculty",
                last_name="User",
                email=faculty_email
            )
            faculty_user.set_password("faculty_password")  # Replace with a secure password
            faculty_role = Role.query.filter_by(name="faculty").first()
            if not faculty_role:
                faculty_role = Role(name="faculty")
                db.session.add(faculty_role)
                db.session.commit()
            faculty_user.roles.append(faculty_role)
            db.session.add(faculty_user)
            db.session.commit()
            print(f"Faculty user with email '{faculty_email}' added successfully.")
        else:
            print(f"Faculty user with email '{faculty_email}' already exists.")

        # Add a student user
        student_email = "student@aui.ma"  # Student email
        existing_student_user = User.query.filter_by(email=student_email).first()

        if not existing_student_user:
            student_user = User(
                first_name="Student",
                last_name="User",
                email=student_email
            )
            student_user.set_password("studentpassword")  # Replace with a secure password
            student_role = Role.query.filter_by(name="student").first()
            if not student_role:
                student_role = Role(name="student")
                db.session.add(student_role)
                db.session.commit()
            student_user.roles.append(student_role)
            db.session.add(student_user)
            db.session.commit()
            print(f"Student user with email '{student_email}' added successfully.")
        else:
            print(f"Student user with email '{student_email}' already exists.")

if __name__ == "__main__":
    add_user()
