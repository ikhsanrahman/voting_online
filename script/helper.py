from datetime import datetime, timedelta
from hashlib import md5

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_time():
    timezone = pytz.timezone("Asia/Jakarta")
    return datetime.now(timezone)

def time2time(time):
    return datetime.strftime(time, "%d-%m-%y %H:%M")

def generate_filename(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    return md5(filename.encode()).hexdigest() + '.'+extension