from datetime import datetime
from sql_connection import get_sql_connection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ------------------ Customers ------------------
def get_customer_id_by_name(connection, customer_name, customer_phone):
    cursor = connection.cursor()
    query = "SELECT customer_id FROM customers WHERE name = %s AND phone = %s"
    cursor.execute(query, (customer_name, customer_phone))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0]
    else:
        # Insert new customer if not found
        cursor = connection.cursor()
        insert_query = "INSERT INTO customers (name, phone) VALUES (%s, %s)"
        cursor.execute(insert_query, (customer_name, customer_phone))
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id


# ------------------ Orders ------------------
def get_all_orders(connection):
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT 
            o.order_id,
            o.total,
            o.datetime,
            c.name AS customer_name,
            c.phone AS customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id DESC
    """

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result


def insert_order(connection, order):
    try:
        cursor = connection.cursor()

        # Get or create customer
        customer_id = get_customer_id_by_name(
            connection,
            order['customer_name'],
            order['customer_phone']
        )

        # Insert into orders
        insert_order_query = """
            INSERT INTO orders (customer_id, total, datetime)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_order_query, (
            customer_id,
            order['grand_total'],
            datetime.now()
        ))
        order_id = cursor.lastrowid

        # Insert order details
        for item in order['order_details']:
            insert_detail_query = """
                INSERT INTO order_details (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_detail_query, (
                order_id,
                item['product_id'],
                item['quantity']
            ))

        connection.commit()
        cursor.close()
        return order_id   # ✅ plain order_id

    except Exception as e:
        connection.rollback()
        print("Error inserting order:", str(e))
        return None   # return None if failed


# ------------------ Invoice Generator ------------------
def generate_invoice_pdf(order_id, connection, filename):
    cursor = connection.cursor(dictionary=True)

    # Get order + customer info
    query = """
        SELECT o.order_id, o.total, o.datetime, 
               c.name AS customer_name, c.phone AS customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
    """
    cursor.execute(query, (order_id,))
    order = cursor.fetchone()

    # Get order items
    query = """
        SELECT p.name AS product_name, od.quantity, p.price_per_unit AS price, 
               (od.quantity * p.price_per_unit) AS subtotal
        FROM order_details od
        JOIN products p ON od.product_id = p.product_id
        WHERE od.order_id = %s
    """
    cursor.execute(query, (order_id,))
    items = cursor.fetchall()
    cursor.close()

    # Create PDF
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Order ID: {order['order_id']}")
    c.drawString(50, 700, f"Customer: {order['customer_name']}")
    c.drawString(50, 680, f"Phone: {order['customer_phone']}")
    c.drawString(50, 660, f"Date: {order['datetime']}")

    # Table header
    y = 630
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product")
    c.drawString(250, y, "Quantity")
    c.drawString(350, y, "Price")
    c.drawString(450, y, "Subtotal")
    y -= 20

    # Table rows
    c.setFont("Helvetica", 12)
    for item in items:
        c.drawString(50, y, item['product_name'])
        c.drawString(250, y, str(item['quantity']))
        c.drawString(350, y, f"{item['price']:.2f}")
        c.drawString(450, y, f"{item['subtotal']:.2f}")
        y -= 20

    # Total
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "Total:")
    c.drawString(450, y, f"{order['total']:.2f}")

    c.save()
    return filename
