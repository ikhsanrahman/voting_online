import os
import csv
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
from models import *

@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == int(id)).first()


@app.route("/")
def index_view():
    # return render_template("login.html")
    candidates = Candidate.query.all()
    return render_template("landing.html", candidates=candidates)


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

# @app.route("/login_admin", methods=["GET", "POST"])
# def login_admin():
#     if request.method == "POST":
#         nim = int(request.form["nim"])
#         if nim:
#             user = User.query.filter_by(nim=nim).first()
#             if user:
#                 login_user(user)
#                 if user.role == "admin":
#                     return redirect(url_for("admin_dashboard"))
#                 return redirect("/evote")
#             else:
#                 app.logger.info("login failed!")
#                 return render_template("login.html", message="error")
#     return render_template("login_admin.html")

@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        try:
            nim = int(request.form["nim"])
        except Exception as e:
            flash("Nim yang dimasukkan salah, silahkan diulangi kembali !!!")
            return render_template("landing.html")

        if nim:
            user = User.query.filter_by(nim=nim).first()
            if user:
                login_user(user)
                if user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect("/evote")
            else:
                app.logger.info("login failed!")
                return redirect("/")
                # return render_template("landing.html", message="error")
    candidates = Candidate.query.all()
    return render_template("landing.html", candidates=candidates)

@app.route("/login_pemilih", methods=["GET", "POST"])
def login_pemilih():
    if request.method == "POST":
        try:
            nim = int(request.form["nim"])
        except Exception as e:
            flash("Silahkan masukkan data dengan benar!!!")
            return render_template("landing.html")

        # birthday = request.form["birthday"]
        email = request.form["email"]
        file = request.files["file"]
        filename = generate_filename(file.filename)
        # if filename in 
        file.save(os.path.join(app.config["UPLOAD_FOLDER"]+"/../ktm", filename))
        
        try: 
            if nim and email and file:
                user = User.query.filter_by(nim=nim, email=email).first()
                if user:
                    # user.birthday = birthday
                    # user.email = email
                    user.selfi = filename
                    db.session.commit()
                    login_user(user)
                    if user.role == "admin":
                        return redirect(url_for("admin_dashboard"))
                    return redirect("/evote")
                else:
                    flash("Silahkan masukkan data dengan benar!!!")
                    return redirect("/")
        except:
            flash("Silahkan masukkan data dengan benar!!!")
            return redirect("/")
    candidates = Candidate.query.all()
    return render_template("landing.html", candidates=candidates)


@app.route("/user/add_code", methods=["GET", "POST"])
@login_required
def add_code_vote():
    if current_user.role == "user":
        if request.method == "POST":
            code = request.form["code"]
            user = current_user
            user.code = code
            db.session.commit()
            flash("Terima kasih susah memasukkan code suara anda")
            return redirect("/evote")


@app.route("/evote")
@login_required
def evote_view():
    if (
        current_user.role == "user"
        and current_user.confirmed == True
        and current_user.voted == False
        and current_user.is_allowed == True
    ):
        candidates = Candidate.query.all()
        return render_template("vote.html", candidates=candidates)
    elif (current_user.role == "user"
        and current_user.confirmed == True
        and current_user.voted == True
        and current_user.is_allowed == True
        ):
        flash("Hak Memilih Sudah digunakan. Terima Kasih")
        return render_template("vote.html")

    else:
        flash("Anda belum di izinkan untuk memilih, Silahkan Datang ke administrasi untuk perizinan")
        return render_template("vote.html")

    if current_user.role == "user" and current_user.voted == True:
        return redirect("/success")
    return redirect("/login")


@app.route("/logout")
@login_required
def logout_user_view():
    logout_user()
    return redirect(url_for("index_view"))


@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role == "admin":
        suara_masuk = User.query.filter_by(voted=True).count()
        total_pemilih = User.query.filter_by(role="user").count()
        print(suara_masuk, total_pemilih)
        try:
            rasio = round(suara_masuk / total_pemilih * 100, 4)
        except:
            rasio = 0
        candidates = [c.name for c in Candidate.query.all()]
        counts = [c.counts for c in Candidate.query.all()]
        return render_template(
            "admin.html",
            page="main-page",
            rasio=rasio,
            candidates=candidates,
            counts=counts,
        )


@app.route("/admin/upload", methods=["GET", "POST"])
@login_required
def upload_peserta():
    if current_user.role == "admin":
        if request.method == "POST":
            file = request.files["file"]
            if file:
                filename = generate_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"]+"/../file", filename))
                file = app.config["UPLOAD_FOLDER"]+f"/../file/{filename}"
                try:
                    with open(file) as f:
                        reader = csv.reader(f)
                        for row in reader:
                            nim = row[1]
                            name = row[3]
                            email = row[4]
                            birthday = row[5]
                            # check user
                            user_exists = User.query.filter_by(nim=int(nim)).first()
                            if not user_exists:
                                u = User(nim=int(nim), name=name, email=email, birthday=birthday)
                                db.session.add(u)
                                db.session.commit()
                            else:
                                pass
                except Exception as e:
                    print(e)
                    flash("Please check your file!")
                    return render_template("admin-upload.html")
                return redirect("/admin/konfirmasi")
        return render_template("admin-upload.html")


@app.route("/admin/candidate", methods=["GET", "POST"])
@login_required
def add_candidate():
    if current_user.role == "admin":
        if request.method == "POST":
            file = request.files["file"]
            name = request.form["name"]
            nim = request.form["nim"]
            visi = request.form["visi"]
            misi = request.form["misi"]
            if file:
                filename = generate_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                cand = Candidate.query.filter_by(name=name).first()
                cand1 = Candidate.query.filter_by(nim=nim).first()
                print(cand, cand1)
                print(not cand, not cand1)
                if not cand and not cand1:
                    u = Candidate(name=name, nim=nim, filename=filename, visi=visi, misi=misi)
                    db.session.add(u)
                    db.session.commit()
                    return redirect("/admin/candidate")
                else:
                    flash("Kandidat sudah di daftarkan")
                    candidates = Candidate.query.all()
                    return render_template("admin-candidates.html", candidates=candidates)

        candidates = Candidate.query.all()
        return render_template("admin-candidates.html", candidates=candidates)


@app.route("/admin/show_candidates", methods=["GET", "POST"])
@login_required
def show_candidate():
    if current_user.role == "admin":
        if request.method == "POST":
            candidates = Candidate.query.all()
            if candidates:
                for cand in candidates:
                    cand.display = True
                    db.session.commit()
            else:
                flash("Tidak ada kandidat yang ditampilkan")
                return redirect("/admin/candidate")

            flash("Kandidat sudah dapat di lihat di halaman depan")
            return redirect("/admin/candidate")


@app.route("/admin/undo_candidates", methods=["GET", "POST"])
@login_required
def undo_candidate():
    if current_user.role == "admin":
        if request.method == "POST":
            candidates = Candidate.query.all()
            if candidates:
                for cand in candidates:
                    cand.display = False
                    db.session.commit()
            else:
                flash("Tidak ada kandidat yang ditarik")
                return redirect("/admin/candidate")

            flash("Kandidat sudah ditarik dari tampilan publik")
            return redirect("/admin/candidate")


@app.route("/admin/konfirmasi")
@login_required
def konfirmasi_voter():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=False).filter_by(role="user").all()
        return render_template("admin-konfirmasi.html", user=user)
    return redirect("/")


@app.route("/admin/hapus/<candidate_id>")
@login_required
def delete_candidate(candidate_id):
    if current_user.role == "admin":
        candidate = Candidate.query.filter_by(id=candidate_id).first()
        db.session.delete(candidate)
        db.session.commit()
        return redirect("/admin/candidate")
    return redirect("/")


@app.route("/admin/confirmed")
@login_required
def confirmed_voter():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=True)\
        .filter_by(role="user")\
        .filter_by(is_allowed=True)\
        .filter_by(vote_is_canceled=False)\
        .all()
        return render_template("admin-confirmed.html", user=user)
    return redirect("/")

@app.route("/admin/unconfirmed/<id_user>")
@login_required
def unconfirmed_voter(id_user):
    if current_user.role == "admin":
        user = User.query.filter_by(id=id_user)\
        .filter_by(role="user").first()
        if user:
            user.confirmed = False
            db.session.commit()
        else:
            pass
        return render_template("admin-confirmed.html", user=user)
    return redirect("/")

@app.route("/admin/is_allowed")
@login_required
def allowed_voter():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=True)\
        .filter_by(is_allowed=False)\
        .filter_by(role="user")\
        .all()
        return render_template("admin-is-allowed.html", user=user)
    return redirect("/")

# admin/bad_vote
@app.route("/admin/bad_vote")
@login_required
def bad_vote():
    if current_user.role == "admin":
        user = User.query.filter_by(confirmed=True)\
        .filter_by(role="user")\
        .filter_by(is_allowed=True)\
        .filter_by(vote_is_canceled=True)\
        .all()
        return render_template("admin-bad-vote.html", user=user)
    return redirect("/")

@app.route("/admin/right_vote/<user_id>", methods=["POST"])
@login_required
def right_vote(user_id):
    if current_user.role == "admin":
        user = User.query.filter_by(id=user_id).first()
        if user:
            candidate_id = user.candidate_id
            candidate = Candidate.query.filter_by(id=candidate_id).first()
            candidate.vote(user)
            db.session.commit()
            user.vote_is_canceled = False
            db.session.commit()
            flash(f"Suara milik {user.name} telah di Sahkan kembali")        
            return redirect("/admin/confirmed")
    return redirect("/")


@app.route("/admin/allow/<id>", methods=["POST"])
@login_required
def allow_voter(id):
    if id:
        u = User.query.filter_by(id=id).first()
        print(u, "is all")
        if u:
            u.is_allowed = True
            db.session.commit()
            return redirect("/admin/konfirmasi")



@app.route("/admin/konfirm/<id>", methods=["POST"])
@login_required
def konfirm_voter(id):
    if id:
        u = User.query.filter_by(id=id).first()
        if u:
            u.confirmed = True
            db.session.commit()
            return redirect("/admin/konfirmasi")

# /admin/cancel_vote/{{u.id}}
@app.route("/admin/cancel_vote/<id>", methods=["POST"])
@login_required
def cancel_vote(id):
    if current_user.role == "admin":
        user = User.query.filter_by(id=id).first()
        if user:
            candidate_id = user.candidate_id
            candidate = Candidate.query.filter_by(id=candidate_id).first()
            candidate.unvote(user)
            db.session.commit()
            flash(f"Suara milik {user.name} telah di batalkan")        
            return redirect("/admin/confirmed")


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
