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

deploy:
	sudo env/bin/gunicorn app:app -b 0.0.0.0:80 -w 3
