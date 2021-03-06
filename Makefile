env:
	source env/bin/activate

init:
	python -c "from app import db; db.create_all(); print('db created')"

dev:
	python app.py

import:
	python script/import-user.py

admin:
	python script/addadmin.py

reset:
	make init
	make import 
	make admin

sim:
	python3 script/vote.py

db_change:
	python3 manage.py db migrate
	python3 manage.py db upgrade

run:
	rm -rf evoted.db migrations
	make init_db
	make add_admin
	make prod


init_db:
# 	python3 -m venv env
# 	source env/bin/activate
	python3 manage.py db init
	python3 manage.py db migrate
	python3 manage.py db upgrade

add_admin:
	python3 manage.py add_admin

prod:
	gunicorn wsgi:app -w 3

reset_vote:
	python3 script/reset-voters.py

