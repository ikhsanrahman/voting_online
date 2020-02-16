import os
from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
    send_from_directory,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from hashlib import md5
from script.helper import allowed_file, current_time, time2time, generate_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///evote.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/img"
app.secret_key = "managaassQW"


login = LoginManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_view"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.Integer, unique=True)
    role = db.Column(db.String(10), default="user")
    name = db.Column(db.String())
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"))
    voted = db.Column(db.Boolean(), default=False)
    confirmed = db.Column(db.Boolean(), default=False)

    def __init__(self, nim: int, name: str) -> None:
        self.nim = nim
        self.name = name

    def is_active(self):
        return True

    def is_authenticated(self) -> bool:
        return True

    def is_anonymous(self) -> bool:
        return True

    def get_id(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return "<User %r>" % (self.nim)

    def set_admin(self):
        self.role = "admin"


class Candidate(db.Model):
    __tablename__ = "candidate"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    filename = db.Column(db.String())
    counts = db.Column(db.Integer(), default=0)
    voters = db.relationship("User", backref="voter", lazy=True)

    def __init__(self, name: str, filename: str):
        self.name = name
        self.filename = filename

    def __repr__(self):
        return "<id {}>".format(self.id)

    def vote(self, voter):
        self.counts += 1
        voter.voted = True
        self.voters.append(voter)


@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == int(id)).first()


@app.route("/")
def index_view():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        nim = int(request.form["nim"])
        if nim:
            user = User.query.filter_by(nim=nim).first()
            if user:
                login_user(user)
                if user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect("/evote")
            else:
                app.logger.info("login failed!")
                return render_template("login.html", message="error")
    return render_template("login.html")


@app.route("/evote")
@login_required
def evote_view():
    if (
        current_user.role == "user"
        and current_user.confirmed == True
        and current_user.voted == False
    ):
        candidates = Candidate.query.all()
        return render_template("vote.html", candidates=candidates)
    if current_user.role == "user" and current_user.voted == True:
        return redirect("/success")
    return redirect("/login")


@app.route("/logout")
@login_required
def logout_user_view():
    logout_user()
    return redirect(url_for("index_view"))


@login_required
@app.route("/admin")
def admin_dashboard():
    if current_user.role == "admin":
        suara_masuk = User.query.filter_by(voted=True).count()
        total_pemilih = User.query.filter_by(role="user").count()
        print(suara_masuk, total_pemilih)
        rasio = round(suara_masuk / total_pemilih * 100, 4)
        print(rasio)
        candidates = [c.name for c in Candidate.query.all()]
        counts = [c.counts for c in Candidate.query.all()]
        return render_template(
            "admin.html",
            page="main-page",
            rasio=rasio,
            candidates=candidates,
            counts=counts,
        )


@app.route("/admin/candidate", methods=["GET", "POST"])
@login_required
def add_candidate():
    if current_user.role == "admin":
        if request.method == "POST":
            file = request.files["file"]
            name = request.form["name"]
            if file:
                filename = generate_filename(file.filename)
                print(filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                u = Candidate(name=name, filename=filename)
                db.session.add(u)
                db.session.commit()
                return redirect("/admin/candidate")
        candidates = Candidate.query.all()
        return render_template("admin-candidates.html", candidates=candidates)


@app.route("/admin/konfirmasi")
@login_required
def konfirmasi_voter():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=False).filter_by(role="user").all()
        return render_template("admin-konfirmasi.html", user=user)
    return redirect("/")


@app.route("/admin/confirmed")
@login_required
def confirmed_voter():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=True).filter_by(role="user").all()
        return render_template("admin-confirmed.html", user=user)
    return redirect("/")


@app.route("/admin/konfirm/<id>", methods=["POST"])
@login_required
def konfirm_voter(id):
    if id:
        u = User.query.filter_by(id=id).first()
        if u:
            u.confirmed = True
            db.session.commit()
            return redirect("/admin/konfirmasi")


@app.route("/vote/<id>", methods=["POST"])
@login_required
def vote(id):
    if current_user.role == "user" and current_user.voted == False:
        c = Candidate.query.filter_by(id=id).first()
        if c:
            c.vote(current_user)
            db.session.commit()
            return redirect("/success")
    return redirect("/success")


@app.route("/success")
@login_required
def success():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)
