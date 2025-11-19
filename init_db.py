# init_db.py
from backend.database import SessionLocal
from backend.models import Base, Voter
from backend.auth import hash_password
from backend.database import engine

# create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
# create admin if not exists
if not db.query(Voter).filter_by(username='admin').first():
    admin = Voter(username='admin', password_hash=hash_password('adminpass'), is_admin=True)
    db.add(admin)
    db.commit()
    print('created admin with username=admin password=adminpass')
else:
    print('admin already exists')
