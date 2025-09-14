from sql_connection import get_sql_connection

def get_all_products(connection):
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT p.product_id, p.name, p.uom_id, p.price_per_unit, u.uom_name
        FROM products p
        LEFT JOIN uom u ON p.uom_id = u.uom_id
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result


def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = (
        "INSERT INTO products (name, uom_id, price_per_unit) "
        "VALUES (%s, %s, %s)"
    )
    data = (product['product_name'], product['uom_id'], product['price_per_unit'])

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid

def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = "DELETE FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    connection.commit()

    return cursor.lastrowid

if __name__ == '__main__':
    connection = get_sql_connection()
    # print(get_all_products(connection))
    # print(insert_new_product(connection, {
        # 'product_name': 'potatoes',
        # 'uom_id': '1',
        # 'price_per_unit': 10
    # }))
