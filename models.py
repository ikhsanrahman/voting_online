from app import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.Integer, unique=True)
    role = db.Column(db.String(10), default="user")
    name = db.Column(db.String())
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"))
    voted = db.Column(db.Boolean(), default=False)
    email = db.Column(db.String(), nullable=True)
    selfi = db.Column(db.String(), nullable=True)
    birthday = db.Column(db.String(), nullable=True)
    confirmed = db.Column(db.Boolean(), default=False)
    code = db.Column(db.String(), nullable=True)
    vote_is_canceled = db.Column(db.Boolean(), default=False)
    is_allowed = db.Column(db.Boolean(), default=False)

    # def __init__(self, nim: int, name: str, birthday: str, email: str) -> None:
    #     self.nim = nim
    #     self.name = name
    #     self.email = email
    #     self.birthday = birthday

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
    nim = db.Column(db.Integer, unique=True)
    visi = db.Column(db.Text)
    misi = db.Column(db.Text)
    display = db.Column(db.Boolean(), default=False)
    counts = db.Column(db.Integer(), default=0)
    voters = db.relationship("User", backref="voter", lazy=True)

    def __init__(self, name: str, filename: str, nim: int, visi: str, misi: str):
        self.name = name
        self.filename = filename
        self.nim = nim
        self.visi = visi
        self.misi = misi

    def __repr__(self):
        return "<id {}>".format(self.id)

    def vote(self, voter):
        self.counts += 1
        voter.voted = True
        self.voters.append(voter)

    def unvote(self, voter):
        self.counts -= 1
        voter.vote_is_canceled = True

