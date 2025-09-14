from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def generate_bill_pdf(order_id, connection, filename="bill.pdf"):
    cursor = connection.cursor()

    # Fetch order header
    cursor.execute("""
        SELECT o.order_id, o.total, o.datetime, c.customer_name 
        FROM orders o 
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
    """, (order_id,))
    order = cursor.fetchone()

    # Create PDF
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height-30, "GROCERY STORE BILL")

    # Order info
    c.setFont("Helvetica", 12)
    c.drawString(30, height-70, f"Order ID: {order[0]}")
    c.drawString(30, height-90, f"Customer: {order[3]}")
    c.drawString(30, height-110, f"Date: {order[2]}")

    # Table headers
    y = height-150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Product")
    c.drawString(200, y, "Qty")
    c.drawString(250, y, "Price")
    c.drawString(320, y, "Total")
    y -= 20
    c.setFont("Helvetica", 12)

    # Fetch order details
    cursor.execute("""
        SELECT p.name, od.quantity, p.price_per_unit, (od.quantity * p.price_per_unit) AS total
        FROM order_details od
        JOIN products p ON od.product_id = p.product_id
        WHERE od.order_id = %s
    """, (order_id,))
    rows = cursor.fetchall()

    for row in rows:
        c.drawString(30, y, str(row[0]))
        c.drawString(200, y, str(row[1]))
        c.drawString(250, y, f"{row[2]:.2f}")
        c.drawString(320, y, f"{row[3]:.2f}")
        y -= 20

    # Grand total
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, f"Grand Total: {order[1]}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 40, "Thank you for shopping with us!")

    # Save PDF
    c.save()
    print(f"✅ Bill saved as {filename}")
