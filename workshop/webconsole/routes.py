from flask import Blueprint, render_template, session, redirect, url_for, request
from webconsole.database import get_engine, User, UserBalance
from sqlalchemy import select, update

bp = Blueprint('main', __name__)

session_engine = get_engine()

@bp.route('/')
def index():
    if ('username' in session):
        return render_template('index.html')
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET','POST'])
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
            session['user_id'] = userdata.user_id
            session['created'] = userdata.created
            session['is_admin'] = userdata.is_admin
            session['allow_prompt'] = userdata.allow_prompt
            session['allow_dalle'] = userdata.allow_dalle
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.index'))

@bp.route('/balance')
def balance():
    if ('username' in session):
        userbalance = '0'
        if session['user_id'] != None:
            userdata = session_engine.scalars(select(UserBalance).where(UserBalance.user_id == session['user_id'])).first()
            userbalance = '0' if userdata == None else str(userdata.balance)
        return render_template('balance.html', userbalance=userbalance)
    return redirect(url_for('main.login'))

@bp.route('/detail')
def detail():
    if ('username' in session):
        return render_template('detail.html')
    return redirect(url_for('main.login'))

@bp.route('/under_construction')
def empty_page():
    if ('username' in session):
        return render_template('empty_page.html')
    return redirect(url_for('main.login'))

@bp.route('/users')
def users():
    if ('username' in session and session['is_admin'] == True):
        user_list = session_engine.scalars(select(User))
        return render_template('users.html', users=user_list)
    return render_template('404.html')

@bp.route('/user/<user_id>', methods=['GET','POST'])
def user_detail(user_id):
    print(request.method)
    print(session)
    if ('username' in session and session['is_admin'] == True):
        if request.method == 'GET':
            _user = session_engine.scalars(select(User).where(User.user_id==user_id)).first()
            return render_template('user_detail.html', user=_user)
        elif request.method == 'POST':
            is_admin = ('is_admin' in request.form)
            allow_prompt = ('allow_prompt' in request.form)
            allow_dalle = ('allow_dalle' in request.form)
            balance = 0 if (request.form['balance']=='') else int(request.form['balance'])
            session_engine.execute(update(User).where(User.user_id==user_id).values(is_admin=is_admin, allow_prompt=allow_prompt, allow_dalle=allow_dalle))
            session_engine.execute(update(UserBalance).where(UserBalance.user_id==user_id).values(balance=balance))
            session_engine.commit()
            return redirect(url_for('main.users'))
    return render_template('404.html')
