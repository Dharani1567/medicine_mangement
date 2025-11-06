from flask import Flask, jsonify, request, render_template
from db_connection import get_db_connection
from datetime import date, timedelta



app = Flask(__name__)
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# ✅ Root route
@app.route('/')
def home():
    return jsonify({"message": "Medical Management API is running!"})


# ✅ Get all medicines
@app.route('/medicines', methods=['GET'])
def get_medicines():
    conn, cur = None, None
    medicines = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM medicines ORDER BY medicine_id;")
            rows = cur.fetchall()
            for row in rows:
                medicines.append({
                    "medicine_id": row[0],
                    "name": row[1],
                    "batch_number": row[2],
                    "expiry_date": str(row[3]),
                    "quantity": row[4],
                    "supplier_id": row[5],
                    "category_id": row[6],
                    "price": float(row[7])
                })
        else:
            return jsonify({"error": "Database connection failed."}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "An error occurred while fetching medicines."}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return jsonify(medicines)


# ✅ Add a new medicine
@app.route('/medicines', methods=['POST'])
def add_medicine():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
        INSERT INTO medicines (name, batch_number, expiry_date, quantity, supplier_id, category_id, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING medicine_id;
        """
        cur.execute(query, (
            data['name'], data['batch_number'], data['expiry_date'],
            data['quantity'], data['supplier_id'], data['category_id'], data['price']
        ))
        conn.commit()
        new_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"message": "Medicine added successfully", "medicine_id": new_id}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error adding medicine"}), 500


# ✅ Update a medicine
@app.route('/medicines/<int:medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
        UPDATE medicines SET
            name = %s,
            batch_number = %s,
            expiry_date = %s,
            quantity = %s,
            supplier_id = %s,
            category_id = %s,
            price = %s
        WHERE medicine_id = %s;
        """
        cur.execute(query, (
            data['name'], data['batch_number'], data['expiry_date'],
            data['quantity'], data['supplier_id'], data['category_id'], data['price'], medicine_id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Medicine updated successfully"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error updating medicine"}), 500


# ✅ Delete a medicine
@app.route('/medicines/<int:medicine_id>', methods=['DELETE'])
def delete_medicine(medicine_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM medicines WHERE medicine_id = %s;", (medicine_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Medicine deleted successfully"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error deleting medicine"}), 500


# ✅ Search medicines
@app.route('/search', methods=['GET'])
def search_medicines():
    query = request.args.get('q', '')
    results = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = """
        SELECT * FROM medicines
        WHERE name ILIKE %s OR batch_number ILIKE %s;
        """
        cur.execute(sql, (f"%{query}%", f"%{query}%"))
        rows = cur.fetchall()
        for row in rows:
            results.append({
                "medicine_id": row[0],
                "name": row[1],
                "batch_number": row[2],
                "expiry_date": str(row[3]),
                "quantity": row[4],
                "supplier_id": row[5],
                "category_id": row[6],
                "price": float(row[7])
            })
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error searching medicines"}), 500


# ✅ Low stock & near-expiry alerts
@app.route('/alerts', methods=['GET'])
def alerts():
    alerts_data = {"low_stock": [], "near_expiry": []}
    today = date.today()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Low stock (quantity < 10)
        cur.execute("SELECT * FROM medicines WHERE quantity < 10;")
        low_stock = cur.fetchall()
        for row in low_stock:
            alerts_data["low_stock"].append({"name": row[1], "quantity": row[4]})
        # Near expiry (within 30 days)
        cur.execute("SELECT * FROM medicines WHERE expiry_date <= %s;", (today + timedelta(days=30),))
        near_expiry = cur.fetchall()
        for row in near_expiry:
            alerts_data["near_expiry"].append({"name": row[1], "expiry_date": str(row[3])})
        cur.close()
        conn.close()
        return jsonify(alerts_data)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error fetching alerts"}), 500


# ✅ Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn, cur = None, None
    users = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users;")
            rows = cur.fetchall()
            for row in rows:
                users.append({
                    "user_id": row[0],
                    "name": row[1],
                    "role": row[2],
                    "email": row[3],
                    "password": row[4]
                })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error fetching users"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return jsonify(users)


if __name__ == '__main__':
    app.run(debug=True)
