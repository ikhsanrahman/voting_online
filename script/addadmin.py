import os
import sys

sys.path.append(os.getcwd())

from app import db, User

admin = User(name="admin", nim=1122334455)
print(admin.role)
db.session.add(admin)
admin.set_admin()
db.session.commit()
print(admin.role)
print(User.query.filter_by(role="admin").first())