from app import db
import fire

def init_db(db=db):
	print(dir(db))

if __name__ == '__main__':
	fire.Fire()
