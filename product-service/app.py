from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="products-db",
        user="root",
        password="rootpassword",
        database="products_db"
    )

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
