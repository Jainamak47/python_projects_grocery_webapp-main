from flask import Flask, request, jsonify, send_file
from sql_connection import get_sql_connection
from invoice_generator import generate_bill_pdf
import json

import products_dao
import orders_dao
import uom_dao

app = Flask(__name__)

connection = get_sql_connection()

# ================== UOM ==================
@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = uom_dao.get_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ================== Products ==================

@app.route('/getProducts', methods=['GET'])
def get_products():
    connection = get_sql_connection()   # new connection
    response = products_dao.get_all_products(connection)
    connection.close()                  # close it
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = json.loads(request.form['data'])
    product_id = products_dao.insert_new_product(connection, request_payload)
    response = jsonify({'product_id': product_id})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    return_id = products_dao.delete_product(connection, request.form['product_id'])
    response = jsonify({'product_id': return_id})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ================== Orders ==================
@app.route('/getAllOrders', methods=['GET'])
def get_all_orders():
    response = orders_dao.get_all_orders(connection)

    # ✅ Normalize field names for frontend
    for order in response:
        order['grand_total'] = order.pop('total', 0)

    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertOrder', methods=['POST'])
def insert_order():
    request_payload = json.loads(request.form['data'])
    order_id = orders_dao.insert_order(connection, request_payload)

    if order_id:
        response = jsonify({'order_id': order_id})
    else:
        response = jsonify({'error': 'Failed to insert order'})

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ================== Invoice ==================
@app.route('/download-invoice/<int:order_id>', methods=['GET'])
def download_invoice(order_id):
    filename = f"invoice_{order_id}.pdf"
    generate_bill_pdf(order_id, connection, filename)  # create the bill
    return send_file(filename, as_attachment=True)

# ================== Run Server ==================
if __name__ == "__main__":
    print("Starting Python Flask Server For Grocery Store Management System")
    app.run(port=5000)
