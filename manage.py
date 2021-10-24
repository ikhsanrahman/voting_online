import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db
from models import User

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def prod():
    host = '0.0.0.0'
    app.run(host=host, port=5000)

@manager.command
def init_db():
    db.create_all()
    print(">> Database is created succesfully")

@manager.command
def add_admin():
    nim = 1122334455
    name = "admin"
    admin = User(name=name, nim=nim, birthday="2021-10-10", email="pemirahimanistik.xyz")
    db.session.add(admin)
    admin.set_admin()
    db.session.commit()
    print(f"admin: {name} is created with nim: {nim}")

# if __name__ == '__main__':
#     manager.run()
