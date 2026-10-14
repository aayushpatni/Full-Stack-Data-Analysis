from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("\n" + "="*50)
    print(f" TOTAL REGISTERED USERS: {len(users)}")
    print("="*50)
    
    if not users:
        print("No users found in the database yet.")
    
    for u in users:
        print(f"• Name: {u.name}")
        print(f"  Email: {u.email}")
        print(f"  Streak: {u.streak} days")
        print("-" * 50)
    print("\n")
