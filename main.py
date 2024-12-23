from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
# import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
app = Flask(__name__)

def encrypt_info(info, secret_key):
    padding_length = 16 - (len(info) % 16)
    padding = bytes([padding_length] * padding_length)
    info = info + padding
    initialization_vector = os.urandom(16)
    cipher = AES.new(secret_key, AES.MODE_CBC, initialization_vector)
    ciphertext = cipher.encrypt(info)
    return initialization_vector + ciphertext

def decrypt_info(encrypted_details, secret_key):
    initialization_vector = encrypted_details[:16]
    ciphertext = encrypted_details[16:]
    cipher = AES.new(secret_key, AES.MODE_CBC, initialization_vector)
    decrypted_details = cipher.decrypt(ciphertext)
    padding_length = decrypted_details[-1]
    return decrypted_details[:-padding_length]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        conn = mysql.connector.connect(
        host="cs6301-db.czspf0jzcgir.us-east-2.rds.amazonaws.com",
        user="admin",
        passwd="utdcs6301",
        database="customer")
        cursor = conn.cursor()
        # query1 = "select * from login"
        # cursor.execute(query1)
        # rr = cursor.fetchall()
        # print(rr)
        with open('rsa_key.pem','r') as f:
            key = RSA.import_key(f.read())

        cipher = PKCS1_OAEP.new(key.publickey())
        ciphertext = cipher.encrypt(password.encode())
        query1 = f"insert into login(username, password) values('{username}','{ciphertext.hex()}');"
        cursor.execute(query1)
        # print(query1)
        conn.commit()
        cursor.close()
        conn.close()
        if password is not None:
            return redirect(url_for('shopping_page'))
    return render_template('login.html')

@app.route('/shopping_page')
def shopping_page():
    return render_template('shopping_page.html')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        conn = mysql.connector.connect(
        host="cs6301-db.czspf0jzcgir.us-east-2.rds.amazonaws.com",
        user="admin",
        passwd="utdcs6301",
        database="customer")
        cursor = conn.cursor()
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        amount = request.form['amount']
        billing_address = request.form['billing_address'] + ' ' + request.form['billing_city'] + ' ' + request.form['billing_state'] + ' ' + request.form['billing_zip']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        with open('rsa_key.pem','r') as f:
            key = RSA.import_key(f.read())

        cipher = PKCS1_OAEP.new(key.publickey())
        ciphertext = cipher.encrypt(password.encode())
        key = b'secret_key_12345'  
        credit_card_number_aes = encrypt_info(card_number.encode(), key)
        credit_card_expiry_month_year_aes = encrypt_info(expiry_date.encode(), key)
        # query1 = f'insert into customer_accounts(name,email,password,credit_card_number,credit_card_expiry_month_year ,billing_address ,shipping_address) values ("{username}","{email}","{ciphertext.hex()}","""{credit_card_number_aes}""","""{credit_card_expiry_month_year_aes}""","{billing_address}","{billing_address}");'
        query1 = 'INSERT INTO customer_accounts (name, email, password, credit_card_number, credit_card_expiry_month_year, billing_address, shipping_address) VALUES (%s, %s, %s, %s, %s, %s, %s);'

        
        values = (username, email, ciphertext.hex(), credit_card_number_aes, credit_card_expiry_month_year_aes, billing_address, billing_address)
        try:
            cursor.execute(query1, values)
            conn.commit()
        except:
            pass
        print(query1)
        
        return redirect(url_for('payment'))
    return render_template('cart.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/payment' , methods=['GET','POST'])
def payment():
    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)
