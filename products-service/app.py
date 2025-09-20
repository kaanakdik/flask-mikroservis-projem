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
                host="products-db",
                user="root",
                password="rootpassword",
                database="products_db"
            )
            return conn
        except Error as e:
            print(f"DB connection failed: {e}. Retrying in {delay}s...")
            attempt += 1
            time.sleep(delay)
    raise Exception("Could not connect to DB after multiple attempts")

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)

@app.route("/products", methods=["POST"])
def create_product():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", 
                   (data["name"], data["price"]))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Product created"}), 201
