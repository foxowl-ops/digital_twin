# app.py (Backend)
from flask import Flask, request, jsonify
import uuid
import time
from datetime import datetime
import random
import sqlite3

app = Flask(__name__)

# Initialize SQLite DB
conn = sqlite3.connect('transactions.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (transaction_id TEXT, user_id TEXT, amount REAL, currency TEXT, 
              merchant_id TEXT, timestamp TEXT, is_fraud INTEGER, 
              payment_gateway TEXT, latency_ms INTEGER, status TEXT)''')
conn.commit()

def fraud_detection(amount, user_id):
    # Simple rule-based fraud detection (replace with ML model)
    if amount > 900:
        return 1  # Flag as fraud
    return 0

@app.route('/process-payment', methods=['POST'])
def process_payment():
    data = request.json
    transaction_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Simulate latency (100ms to 5s)
    latency_ms = random.randint(100, 5000)
    time.sleep(latency_ms / 1000)  # Simulate processing time
    
    # Fraud detection
    is_fraud = fraud_detection(data['amount'], data['user_id'])
    
    # Approve/decline logic
    status = "success" if (is_fraud == 0 and data['amount'] <= 1000) else "failed"
    
    # Save to DB
    c.execute('''INSERT INTO transactions VALUES 
              (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (transaction_id, data['user_id'], data['amount'], data['currency'],
               data['merchant_id'], timestamp, is_fraud, 
               data['payment_gateway'], latency_ms, status))
    conn.commit()
    
    return jsonify({
        "transaction_id": transaction_id,
        "status": status,
        "latency_ms": latency_ms,
        "is_fraud": is_fraud
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)