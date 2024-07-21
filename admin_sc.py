from alien_tech import app, db
from alien_tech.models import User
# Create the application context
with app.app_context():
    # Now you can perform operations that require the application context
    db.create_all()
    
    
# Check if the admin user already exists
    admin = User.query.filter_by(email="bikorimanadesire@yahoo.com").first()
    if not admin:
        # Create the admin user
        admin = User(
            username="Desire Bikorimana",
            email="bikorimanadesire@yahoo.com",
            is_admin=True
        )
        admin.set_password("Desire@#1")

        # Add admin user to the session and commit
        db.session.add(admin)
        db.session.commit()

        print("Admin user added.")
    else:
        print("Admin user already exists.")