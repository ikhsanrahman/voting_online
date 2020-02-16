import os
import sys

sys.path.append(os.getcwd())

from app import db, User, Candidate

user = User.query.filter_by(role="user").filter_by(voted=False).all()
candidate = Candidate.query.all()

c = candidate[2]

for u in user:
	c.vote(u)
	db.session.commit()
