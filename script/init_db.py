import sys, os

sys.path.append(os.getcwd())
from app import db

db.create_all()