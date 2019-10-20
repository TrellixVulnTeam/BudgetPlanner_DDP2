import sqlite3
import hashlib
from random import randint
from base64 import b64encode
from os import urandom
from Application.send_email import *
from Application.config import settings

admin_email = settings['email']
admin_password = settings['email_password']

def connect_to_db():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                   (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username varchar(32) NOT NULL,
                     password varchar(128) NOT NULL,
                     salt varchar(128) NOT NULL,
                     confirmation varchar(128) NOT NULL,
                     email varchar(128) NOT NULL,
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL);''')
    return connection,cursor
    
def login(username, password):
    connection,cursor = connect_to_db()
    cursor.execute("SELECT password,salt FROM users WHERE username=?", [username])
    rows = cursor.fetchall()

    if not rows:
        return "user does not exist"

    try:
        hashed_password = rows[0][0]
        salt = rows[0][1]
        
        hashed_password_attempt = hash_password(password,salt)

        if hashed_password == hashed_password_attempt:
            #create cookie and redirect to secure pages
            #request.session['username'] = username
            return "login successful"
        else:
            return "incorrect password"
    except:
        return "error logging in"
        

def register_user(username, email, password, password_confirm):
    salt = b64encode(urandom(96)).decode("utf-8")
    hashed_password = hash_password(password, salt)
    connection,cursor = connect_to_db()
    confirmation_code = b64encode(urandom(12)).decode("utf-8").replace("=","a").replace("+","b").replace("/","c")
    confirmation_link = settings['web_address']+"/confirm_email?cc="+confirmation_code+"&user="+username
    name_taken = bool(cursor.execute("SELECT username FROM users WHERE username=?", [username]).fetchall())
    
    if not name_taken: # username is not already taken
        if password != password_confirm:
            return "password doesn't match confirmation password"
        cursor.execute("INSERT INTO users(username, password, salt, confirmation, email) VALUES (?,?,?,?,?)",[username,hashed_password,salt,confirmation_code,email])
        connection.commit()
        connection.close()
            
        email_status = send_email(admin_email,admin_password,email,"Confirmation Email",confirmation_link)
        
        if email_status:
            return "registration successful"
        else:
            return "registration successful, email failed to send"
    else:
        return "username is already in use"

def hash_password(password,salt):
    salted_str = (password+salt).encode("utf-8")
    hashGen = hashlib.sha512()
    hashGen.update(salted_str)
    hashed_password = hashGen.hexdigest()
    return hashed_password

print(login("admin4","password"))
print(register_user("admin4", "budgetplannerswe@gmail.com", "password", "password"))
print(login("admin4","password"))
