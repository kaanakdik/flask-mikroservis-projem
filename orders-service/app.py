import time
from mysql.connector import Error
import mysql.connector
from flask import Flask, request, jsonify

import requests

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
                host="orders-db",
                user="root",
                password="rootpassword",
                database="orders_db"
            )
            return conn
        except Error as e:
            print(f"DB connection failed: {e}. Retrying in {delay}s...")
            attempt += 1
            time.sleep(delay)
    raise Exception("Could not connect to DB after multiple attempts")

@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(orders)

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    user_id = data["user_id"]
    product_id = data["product_id"]

    # 1. Kullanıcı doğrula (users-service üzerinden)
    try:
        user_resp = requests.get(f"http://users-service:5000/users")
        if user_resp.status_code != 200:
            return jsonify({"error": "User service error"}), 500
        users = user_resp.json()
        if not any(u["id"] == user_id for u in users):
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"User service unreachable: {str(e)}"}), 500

    # 2. Ürün doğrula (products-service üzerinden)
    try:
        prod_resp = requests.get(f"http://products-service:5000/products")
        if prod_resp.status_code != 200:
            return jsonify({"error": "Product service error"}), 500
        products = prod_resp.json()
        if not any(p["id"] == product_id for p in products):
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Product service unreachable: {str(e)}"}), 500

    # 3. Siparişi kaydet
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, product_id) VALUES (%s, %s)", 
                   (user_id, product_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Order created"}), 201
