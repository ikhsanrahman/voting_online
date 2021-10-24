import os
import sys

sys.path.append(os.getcwd())

from app import db, User, Candidate

candidates = Candidate.query.all()

for c in candidates:
	c.voters = []
	c.counts = 0
	db.session.commit()

voters = User.query.filter_by(role="user").all()

for voter in voters:
	voter.voted = False
	db.session.commit()