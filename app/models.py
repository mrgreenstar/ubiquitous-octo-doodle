from datetime import datetime
from random import randint
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.rsaC import rsaDM
from app import db
from app import login
#pylint: disable=E1101

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    billfolds = db.relationship('Billfold', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username) 

class Billfold(UserMixin, db.Model):
    billfold_number = db.Column(db.String(200), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    wallet = db.Column(db.String(30))                       # Наименование валюты
    balance = db.Column(db.Float)                           # Баланс

    def create_billfold(self, wallet):
        wallets = {"Рубли":"RB", "Доллары":"DL", "Евро":"ER"}
        self.billfold_number = wallets.get(wallet) + datetime.now().strftime("%d%H%M%S")
        self.billfold_number = self.billfold_number[:10]
        self.wallet = wallet

    def __repr__(self):
        return "<Billfold {}>".format(self.billfold_number)

class Transactions(UserMixin, db.Model):
    transactionId = db.Column(db.Integer, primary_key=True, unique=True)
    senderId = db.Column(db.Integer)                        # Id отправителя
    receiverId = db.Column(db.Integer)                      # Id получателя
    senderBill = db.Column(db.String(200))                  # Номер счета отправителя
    receiverBill = db.Column(db.String(200))                # Номер счета получателя
    transferAmount = db.Column(db.String(200))              # Сумма перевода
    message = db.Column(db.String(1200))                    # Сообщение
    date = db.Column(db.String(1200))                       # Дата перевода

    def __repr__(self):
        return "<Transaction with senderId {}>".format(self.senderId)

class CryptoInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer)
    key = db.Column(db.String(1500))

    def __repr__(self):
        return "<Key with user_id {}>".format(self.user_id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))