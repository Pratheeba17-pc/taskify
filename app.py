from db import db_connection
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash,check_password_hash

app= Flask(__name__)
app.secret_key="12345678"

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn=db_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute("select * from tasks where user_id=%s order by created_at DESC",(session['user_id'],))
    tasks=cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html',tasks=tasks,username=session['username'])


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        conn=db_connection()
        cur=conn.cursor()
        cur.execute("select id from users where username=%s",(username,))
        if cur.fetchone():
            flash("Username already exists")
            return redirect(url_for('register'))
        cur.execute("insert into users (username,password) values (%s,%s)",(username,generate_password_hash(password)))
        conn.commit()
        cur.close()
        conn.close()
        flash("Registration Successfull!")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        conn=db_connection()
        cur=conn.cursor(dictionary=True)
        cur.execute("select *  from users where username=%s",(username,))
        user=cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['password'],password):
            session['user_id']=user['id']
            session['username']=user['username']
            flash("Login Successfull!")
            return redirect(url_for('home'))
        else:
            flash("Invalid Credentials")
            

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('login'))

@app.route('/add_task',methods=['POST'])
def add_task():
    task_name=request.form['title']
    conn=db_connection()
    cur=conn.cursor()
    cur.execute("insert into tasks (user_id,title) values (%s,%s)",(session['user_id'],task_name))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn=db_connection()
    cur=conn.cursor()
    cur.execute("delete from tasks where id=%s and user_id=%s",(task_id,session['user_id']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('home'))


@app.route('/completed/<int:task_id>',methods=['POST'])
def completed(task_id):
    conn=db_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute("select completed from tasks where id=%s and user_id=%s",(task_id,session['user_id']))
    task=cur.fetchone()
    if task:
        
        new_status=not task['completed']
        cur.execute("update tasks set completed=%s where id=%s",(new_status,task_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "success":True,
            "completed":new_status
        })
    return jsonify({"success":False}),403
    
# 🔴 NEW ROUTE - Delete User Account
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash("You must be logged in to delete your account","error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = db_connection()
    cur = conn.cursor()

    # delete tasks first (if foreign key constraints not set to cascade)
    cur.execute("DELETE FROM tasks WHERE user_id=%s", (user_id,))
    # delete user
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    session.clear()
    flash("Your account and all tasks have been deleted successfully.","success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)



