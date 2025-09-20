import time
from mysql.connector import Error
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection(retries=5, delay=5):
    """
    MySQL veritabanına bağlanmayı dener.
    retries: kaç kez denenecek
    delay: her deneme arasında kaç saniye bekleyecek
    """
    attempt = 0
    while attempt < retries:
        try:
            conn = mysql.connector.connect(
                host="users-db",
                user="root",
                password="rootpassword",
                database="users_db"
            )
            return conn
        except Error as e:
            print(f"DB connection failed: {e}. Retrying in {delay}s...")
            attempt += 1
            time.sleep(delay)
    raise Exception("Could not connect to DB after multiple attempts")

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", 
                   (data["name"], data["email"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User created"}), 201
