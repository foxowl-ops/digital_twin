# dashboard.py (Frontend)
import streamlit as st
import requests
import pandas as pd
import time
import sqlite3
import numpy as np
import plotly.express as px

st.title("Payment Gateway Digital Twin")

# Mock Payment Form
with st.form("payment_form"):
    user_id = st.text_input("User ID", value="user_123")
    amount = st.number_input("Amount", min_value=1.0, value=100.0)
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP"])
    merchant_id = st.text_input("Merchant ID", value="merchant_456")
    payment_gateway = st.selectbox("Gateway", ["Gateway_A", "Gateway_B"])
    submitted = st.form_submit_button("Submit Payment")

if submitted:
    # Send payment to backend
    response = requests.post(
        'http://localhost:5000/process-payment',
        json={
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "merchant_id": merchant_id,
            "payment_gateway": payment_gateway
        }
    )
    result = response.json()
    st.success(f"Payment {result['status']}! Transaction ID: {result['transaction_id']}")

# Real-Time Dashboard
conn = sqlite3.connect('transactions.db')
df = pd.read_sql_query("SELECT * FROM transactions", conn)

# Create analysis section
st.subheader("Transaction Analytics")

if not df.empty:
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

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()