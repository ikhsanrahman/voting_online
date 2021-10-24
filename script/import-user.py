import os
import sys
import csv
sys.path.append(os.getcwd())
from app import db, User

fisika_csv = os.getcwd()+"/data/fisika.csv"

num_user = 0

with open(fisika_csv) as f:
	# nim on index 1
	# name on index 3
	reader = csv.reader(f)

	for row in reader:
		nim = row[1]
		name = row[3]
		u = User(nim=int(nim), name=name)
		db.session.add(u)
		db.session.commit()
		num_user += 1

print(f"done exporting {num_user}")
