from flask import Flask, render_template, session, redirect, url_for, request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import DateTime, Integer, String, Numeric, ForeignKey, select, update, create_engine, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

import logging

class Base(DeclarativeBase):
  pass

app = Flask(__name__)
app.secret_key = 'some_strong_secret_key'

engine = create_engine("postgresql://postgres:123456aA@192.144.12.140/botconsole", echo=True)

class User(Base):
    __tablename__ = "user"

    id: Mapped[BIGINT] = mapped_column(BIGINT, primary_key=True)
    userid: Mapped[str] = mapped_column(String(120), unique=True)
    username: Mapped[str] = mapped_column(String(120))
    email: Mapped[str]
    created = mapped_column(DateTime, nullable=False)
    is_admin: Mapped[bool]
    allow_prompt: Mapped[bool]
    allow_dalle: Mapped[bool]

    user_balance: Mapped["UserBalance"] = relationship(back_populates="user")

class UserBalance(Base):
    __tablename__ = "user_balance"

    userbalance_id = mapped_column(BIGINT, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey("user.id"))
    balance = mapped_column(Numeric)
    
    user: Mapped["User"] = relationship(back_populates="user_balance")

class UserBalanceDetail(Base):
    __tablename__ = "user_balance_detail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(BIGINT, ForeignKey("user.id"))
    operation_date = mapped_column(DateTime, nullable=False)
    incoming = mapped_column(Numeric)
    outcoming = mapped_column(Numeric)

#Base.metadata.create_all(engine)
session_engine = Session(engine)

@app.route('/')
def index():
    if ('username' in session):
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['user_id'] = None
        session['created'] = None
        session['is_admin'] = False
        session['allow_prompt'] = False
        session['allow_dalle'] = False
        userdata = session_engine.scalars(select(User).where(User.username == session['username'])).first()
        if userdata != None:
            session['user_id'] = userdata.id
            session['created'] = userdata.created
            session['is_admin'] = userdata.is_admin
            session['allow_prompt'] = userdata.allow_prompt
            session['allow_dalle'] = userdata.allow_dalle
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/balance')
def balance():
    if ('username' in session):
        userdata = session_engine.scalars(select(UserBalance).where(UserBalance.user_id == session['user_id'])).first()
        userbalance = '0' if userdata == None else str(userdata.balance)
        return render_template('balance.html', userbalance=userbalance)
    return redirect(url_for('login'))

@app.route('/detail')
def detail():
    if ('username' in session):
        return render_template('detail.html')
    return redirect(url_for('login'))

@app.route('/under_construction')
def empty_page():
    if ('username' in session):
        return render_template('empty_page.html')
    return redirect(url_for('/login'))

@app.route('/users')
def users():
    if ('username' in session and session['is_admin'] == True):
        user_list = session_engine.scalars(select(User))
        return render_template('users.html', users=user_list)
    return render_template('404.html')

@app.route('/user/<user_id>', methods=['GET','POST'])
def user_detail(user_id):
    print(request.method)
    print(session)
    if ('username' in session and session['is_admin'] == True):
        if request.method == 'GET':
            _user = session_engine.scalars(select(User).where(User.id==user_id)).first()
            return render_template('user_detail.html', user=_user)
        elif request.method == 'POST':
            is_admin = ('is_admin' in request.form)
            allow_prompt = ('allow_prompt' in request.form)
            allow_dalle = ('allow_dalle' in request.form)
            balance = 0 if (request.form['balance']=='') else int(request.form['balance'])
            session_engine.execute(update(User).where(User.id==user_id).values(is_admin=is_admin, allow_prompt=allow_prompt, allow_dalle=allow_dalle))
            session_engine.execute(update(UserBalance).where(UserBalance.user_id==user_id).values(balance=balance))
            session_engine.commit()
            return redirect(url_for('users'))
    return render_template('404.html')


if (__name__ == '__main__'):
    app.run()