# online_dashboard.py (Frontend with Mock Backend)
import streamlit as st
import pandas as pd
import time
import numpy as np
import plotly.express as px
import uuid
from datetime import datetime
import random

# Initialize session state for storing transactions
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Mock backend function
def process_payment_mock(payment_data):
    transaction_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    latency_ms = random.randint(100, 5000)
    time.sleep(latency_ms / 1000)  # Simulate processing time
    
    # Simple fraud detection
    is_fraud = 1 if payment_data['amount'] > 900 else 0
    
    # Approve/decline logic
    status = "success" if (is_fraud == 0 and payment_data['amount'] <= 1000) else "failed"
    
    # Create transaction record
    transaction = {
        'transaction_id': transaction_id,
        'user_id': payment_data['user_id'],
        'amount': payment_data['amount'],
        'currency': payment_data['currency'],
        'merchant_id': payment_data['merchant_id'],
        'timestamp': timestamp,
        'is_fraud': is_fraud,
        'payment_gateway': payment_data['payment_gateway'],
        'latency_ms': latency_ms,
        'status': status
    }
    
    # Store in session state
    st.session_state.transactions.append(transaction)
    
    return {
        "transaction_id": transaction_id,
        "status": status,
        "latency_ms": latency_ms,
        "is_fraud": is_fraud
    }

st.set_page_config(
    page_title="Digital Twin Payment Gateway",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .payment-option {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .payment-option:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    .big-title {
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 30px;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">Digital Twin Payment Gateway</p>', unsafe_allow_html=True)

# Initialize session state for payment method
if 'payment_method' not in st.session_state:
    st.session_state.payment_method = None

# Landing page with payment options
if st.session_state.payment_method is None:
    st.write("### Choose your payment method")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💳 Credit/Debit Card", use_container_width=True):
            st.session_state.payment_method = "card"
        if st.button("🏦 Net Banking", use_container_width=True):
            st.info("Net Banking option coming soon!")
            
    with col2:
        if st.button("📱 UPI", use_container_width=True):
            st.info("UPI payment option coming soon!")
        if st.button("💰 Wallet", use_container_width=True):
            st.info("Wallet option coming soon!")

    # Show some additional information
    st.markdown("---")
    st.markdown("### Secure Payment Gateway")
    
    # Display security features and benefits
    sec_col1, sec_col2, sec_col3 = st.columns(3)
    with sec_col1:
        st.markdown("🔒 **End-to-End Encryption**")
        st.write("Your payment data is fully encrypted and secure")
    with sec_col2:
        st.markdown("✅ **PCI DSS Compliant**")
        st.write("We follow the highest security standards")
    with sec_col3:
        st.markdown("⚡ **Quick Checkout**")
        st.write("Fast and seamless payment experience")

# Show payment form only when card is selected
elif st.session_state.payment_method == "card":
    st.markdown("### Credit/Debit Card Payment")
    
    # Add a back button
    if st.button("← Back to Payment Methods"):
        st.session_state.payment_method = None
        st.rerun()

    # Mock Payment Form
    with st.form("payment_form"):
        user_id = st.text_input("Card Holder Name", value="John Doe")
        st.text_input("Card Number", value="4111 1111 1111 1111")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Expiry Date", value="MM/YY")
        with col2:
            st.text_input("CVV", value="***", type="password")
        
        amount = st.number_input("Amount", min_value=1.0, value=100.0)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP"])
        merchant_id = st.text_input("Merchant ID", value="merchant_456")
        payment_gateway = st.selectbox("Payment Processor", ["Visa", "Mastercard", "American Express"])
        submitted = st.form_submit_button("Pay Now")

    if submitted:
        # Use mock backend
        payment_data = {
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "merchant_id": merchant_id,
            "payment_gateway": payment_gateway
        }
        result = process_payment_mock(payment_data)
        st.success(f"Payment {result['status']}! Transaction ID: {result['transaction_id']}")

# Show analytics only if there's data
if st.session_state.transactions:
    st.markdown("---")
    st.subheader("Transaction Analytics")

    # Convert transactions to DataFrame
    df = pd.DataFrame(st.session_state.transactions)
    
    # Create output_data DataFrame with required metrics
    output_data = pd.DataFrame({
        'transaction_id': df['transaction_id'],
        'latency': df['latency_ms'],
        'amount': df['amount'],
        'status': df['status'],
        'is_fraud': df['is_fraud'].apply(lambda x: 'Fraud' if x == 1 else 'Normal')
    })

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", len(output_data))
    with col2:
        st.metric("Average Latency", f"{output_data['latency'].mean():.0f}ms")
    with col3:
        st.metric("Total Amount", f"${output_data['amount'].sum():.2f}")
    with col4:
        fraud_rate = (output_data['is_fraud'] == 'Fraud').mean() * 100
        st.metric("Fraud Rate", f"{fraud_rate:.1f}%")

    # Create visualizations
    st.subheader("Transaction Visualizations")

    # Latency Distribution
    fig_latency = px.histogram(
        output_data, 
        x='latency',
        title='Latency Distribution',
        labels={'latency': 'Latency (ms)'},
        color_discrete_sequence=['#3366cc']
    )
    st.plotly_chart(fig_latency)

    # Amount Distribution by Status
    fig_amount = px.bar(
        output_data, 
        x='status',
        y='amount',
        title='Transaction Amounts by Status',
        color='status',
        labels={'amount': 'Amount ($)', 'status': 'Status'}
    )
    st.plotly_chart(fig_amount)

    # Fraud Distribution
    fig_fraud = px.pie(
        output_data, 
        names='is_fraud',
        title='Transaction Fraud Distribution',
        color_discrete_sequence=['#00cc96', '#ef553b']
    )
    st.plotly_chart(fig_fraud)

    # Display raw data
    st.subheader("Raw Transaction Data")
    st.dataframe(df)
else:
    st.warning("No transaction data available yet.")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun() 