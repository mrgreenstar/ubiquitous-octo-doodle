import sys
import datetime
from app.rsaC.rsaDM import generate_keys, encrypt_message, decrypt_message, generate_public, base_decode
from flask import render_template, flash, redirect, url_for, request
from sqlalchemy import and_
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Billfold, Transactions, CryptoInfo
from app.forms import LoginForm, newBillfold, upBillfold, deleteBillfold, TransferMoney, RegistrationForm
from app import db
from app import app
#pylint: disable=E1101

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user)
        return redirect('main')
    return render_template('login.html', title='Sign in', form=form)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user=User(name=form.first_name.data, surname=form.second_name.data,
            phone_number=form.phone.data, email=form.email.data)
        if len(user.name) >= 100 or len(user.surname) >= 100:
            flash('Слишком длинное имя/фамилия')
            return redirect('registration')
        user.set_password(form.password.data)
        private_key, public_key = generate_keys()
        newKeys = CryptoInfo()
        newKeys.key = str(private_key['priv_exp']) + '|' + str(
                private_key['modulus']) + '|' + str(
                private_key['p']) + '|' + str(private_key['q'])
        
        user.phone_number = encrypt_message(str(form.phone.data), public_key)
        db.session.add(user)
        db.session.commit()
        db.session.add(newKeys)
        newKeys.user_id = user.id
        db.session.commit()
        flash ('Регистрация завершена')
        return redirect(url_for('login'))
    return render_template("registration.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/newBill', methods=['GET', 'POST'])
@login_required
def newBill():
    """
    Функция для добавления новых счетов для пользователя.

    100% можно сделать намного красивее и безопаснее
    + очевидно, что надо добавить защиту от sql injection
    """
    if not current_user.is_authenticated:
        redirect (url_for('login'))
    form = newBillfold()
    
    if form.validate_on_submit():
        try:
            summ = float(form.summ.data)
        except ValueError:
            flash('Некорректная сумма. Попробуйте снова')
            return redirect(url_for('newBill'))
        else:
            bill = Billfold(user_id = current_user.id, balance = summ)
            bill.create_billfold(wallet = form.wallets.data)
            db.session.add(bill)
            db.session.commit()
            return redirect(url_for('main'))
    return render_template("newBill.html", form=form)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """
    Функция для осуществления переводов между пользователями.

    """
    private_key_sender = CryptoInfo.query.filter(CryptoInfo.user_id == current_user.id).first()
    private_key_sender = base_decode(private_key_sender)

    info = [(i.billfold_number,'Счёт №' + i.billfold_number + ' | '
        + str(i.wallet)) for i in Billfold.query.filter(
                Billfold.user_id == current_user.id)]
    
    form = TransferMoney()
    form.bills.choices = info

    if form.bills.data and form.validate_on_submit():
        newTransaction = Transactions()
        newTransaction.senderId = int(current_user.id)
        newTransaction.senderBill = str(form.bills.data)
        newTransaction.receiverBill = str(form.transBill.data)
        newTransaction.receiverId = Billfold.query.filter(
                Billfold.billfold_number == newTransaction.receiverBill).first()

        if newTransaction.receiverId is None:
            flash('Данного счета не существует.')
            return redirect(url_for('transfer'))
        newTransaction.receiverId = newTransaction.receiverId.user_id
        try:
            newTransaction.transferAmount = float(form.transSum.data)
        except ValueError:
            flash('Введите корректную сумму')
            return redirect(url_for('transfer'))
        else:
            sender = Billfold.query.filter(Billfold.billfold_number == 
                    newTransaction.senderBill).first()
            receiver = Billfold.query.filter(Billfold.user_id == newTransaction.receiverId,
                       Billfold.billfold_number == newTransaction.receiverBill).first()
            if newTransaction.transferAmount > sender.balance:
                flash('На вашем счету недостаточно средств.')
                return redirect(url_for('transfer'))

            elif newTransaction.transferAmount <= 0:
                flash('Сумма перевода не может быть отрицательной или меньшей нуля.')
                return redirect(url_for('transfer'))

            elif sender.wallet != receiver.wallet:
                flash('Валюты на счету отправителя и получателя не совпадают.')
                return redirect(url_for('transfer'))

            elif newTransaction.transferAmount <= sender.balance:
                # Информация для отладки
                #print("Сумма перевода: {}\n".format(newTransaction.transferAmount))
                #print("Валюты на счетах отправителя и получателя: {} и {}".format(
                    sender.wallet, receiver.wallet))
                # Конец информации

                user_balance = Billfold.query.filter(Billfold.user_id == current_user.id,\
                            Billfold.billfold_number == newTransaction.senderBill).first()
                user_balance.balance = user_balance.balance - newTransaction.transferAmount

                receiver_balace = Billfold.query.filter(Billfold.user_id\
                        == newTransaction.receiverId, Billfold.billfold_number ==\
                        newTransaction.receiverBill).first()
                receiver_balace.balance = receiver_balace.balance + newTransaction.transferAmount
                db.session.commit()

                decrypted_message = str(form.message.data)

                private_key = CryptoInfo.query.filter(CryptoInfo.user_id == newTransaction.receiverId).first()
                newKey = CryptoInfo()
                if private_key:
                    private_key = base_decode(private_key)
                    public_key=generate_public(private_key)
                else:
                    private_key, public_key = generate_keys()
                    newKey.key = str(private_key['priv_exp']) + '|' + str(
                        private_key['modulus']) + '|' + str(
                        private_key['p']) + '|' + str(private_key['q'])
                    newKey.user_id = int(newTransaction.receiverId)
                    db.session.add(newKey)
                newTransaction.transferAmount = encrypt_message(
                    str(newTransaction.transferAmount), public_key)
                encrypted_message = encrypt_message(decrypted_message, public_key)
                newTransaction.message = encrypted_message
                newTransaction.date = str(datetime.datetime.utcnow())[:19]
                newTransaction.date = encrypt_message(newTransaction.date, public_key)
                db.session.add(newTransaction)
                db.session.commit()
                return redirect(url_for('main'))
    return render_template('transfer.html', form=form)

@app.route('/transactions')
@login_required
def transactions():
    """
    Функция для отображения истории переводов.

    Переписать поиск по базе(откровенный говнокод).
    """
    if not current_user.is_authenticated:
        redirect (url_for('login'))
    sended = []
    received = []
    # Отображение истории для отправителя
    for i in Transactions.query.filter(Transactions.senderId == current_user.id):
        bill_wallet = Billfold.query.filter(Billfold.user_id == current_user.id,
            Billfold.billfold_number == i.senderBill).first().wallet
        sender_key = CryptoInfo.query.filter(CryptoInfo.user_id == current_user.id).first()
        sender_key = base_decode(sender_key)        

        receiver_key = CryptoInfo.query.filter(CryptoInfo.user_id == i.receiverId).first()
        receiver_key = base_decode(receiver_key)
        
        i.message = decrypt_message(i.message, receiver_key)
        i.transferAmount = decrypt_message(i.transferAmount, receiver_key)
        i.date = decrypt_message(i.date, receiver_key)
        i.date = datetime.datetime.strptime(i.date,'%Y-%m-%d %H:%M:%S')
        #i.senderBill = decrypt_message(i.senderBill, sender_key)
        #i.receiverBill = decrypt_message(i.receiverBill, receiver_key)
        sended.append((i, bill_wallet))
    # Отображение истории для получателя
    for i in Transactions.query.filter(Transactions.receiverId == current_user.id):
        bill_wallet = Billfold.query.filter(Billfold.user_id == current_user.id,
            Billfold.billfold_number == i.receiverBill).first().wallet

        receiver_key = CryptoInfo.query.filter(CryptoInfo.user_id == current_user.id).first()
        receiver_key = base_decode(receiver_key)
        sender_key = CryptoInfo.query.filter(CryptoInfo.user_id == i.senderId).first()
        sender_key = base_decode(sender_key)

        i.message = decrypt_message(i.message, receiver_key)
        i.transferAmount = decrypt_message(i.transferAmount, receiver_key)
        i.date = decrypt_message(i.date, receiver_key)
        i.date = datetime.datetime.strptime(i.date,'%Y-%m-%d %H:%M:%S')
        #i.senderBill = decrypt_message(i.senderBill, sender_key)
        #i.receiverBill = decrypt_message(i.receiverBill, receiver_key)

        received.append((i, bill_wallet))

    return render_template('transactions.html', sended=sended, received=received)

@app.route('/upBill', methods=['GET', 'POST'])
@login_required
def upBill():
    """
    Функция для пополнения счета.

    """
    if not current_user.is_authenticated:
        redirect (url_for('login'))
    form = upBillfold()
    private_key = CryptoInfo.query.filter(CryptoInfo.user_id == current_user.id).first()
    private_key = base_decode(private_key)
    bills = [(i.billfold_number,'Счёт №' + i.billfold_number + ' | ' + str(i.wallet))
            for i in Billfold.query.filter(Billfold.user_id == current_user.id)]
    form.bills.choices = bills

    if db.session.query(Billfold.billfold_number, Billfold.balance, Billfold.wallet).\
                                filter(Billfold.user_id == current_user.id):
        Flag = 1
    
    if form.validate_on_submit():
        billNum = str(form.bills.data)
        try:
            summ = float(form.upSumm.data)
        except ValueError:
            flash('Ошибка при вводе суммы')
            return redirect(url_for('upBill'))
        else:
            user_balance = Billfold.query.filter(Billfold.user_id == current_user.id,
                            Billfold.billfold_number == billNum).first()
            if user_balance is not None and summ > 0:
                user_balance.balance = user_balance.balance + summ
                db.session.commit()
            elif summ <= 0:
                flash('Сумма пополнения не может быть меньше или равной нулю')
                return redirect(url_for('upBill'))
            return redirect(url_for('main'))
    return render_template('upBill.html', Flag=Flag, form=form)

@app.route('/main')
@login_required
def main():
    if not current_user.is_authenticated:
        redirect (url_for('login'))

    Flag = 0
    bills = []
    bill_existence = Billfold.query.filter(
        Billfold.user_id == current_user.id).first()
    if bill_existence:
        Flag = 1
        private_key = CryptoInfo.query.filter(
            CryptoInfo.user_id == current_user.id).first()
        private_key = base_decode(private_key)
        for i in Billfold.query.filter(Billfold.user_id == current_user.id):
            bills.append(i)
    return render_template("main.html", user=current_user, Flag=Flag, bills=bills)