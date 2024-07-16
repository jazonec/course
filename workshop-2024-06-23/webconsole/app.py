from flask import Flask, render_template, session, redirect, url_for, request
app = Flask(__name__)
app.secret_key = 'some_strong_secret_key'

@app.route('/')
def index():
    if ('username' in session):
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/balance')
def balance():
    if ('username' in session):
        return render_template('balance.html')
    return redirect(url_for('login'))

@app.route('/detail')
def detail():
    if ('username' in session):
        return render_template('detail.html')
    return redirect(url_for('login'))

if (__name__ == '__main__'):
    app.run()