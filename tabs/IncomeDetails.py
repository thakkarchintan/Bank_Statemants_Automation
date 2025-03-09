import streamlit as st
from datetime import date
from database import *

def income_details():
    st.header("Income")
    st.markdown("Use this section to list down all primary sources of income without considering income from investments and assets.")

    username = st.session_state.get("username") 

    # Create a form for income input
    with st.form("income_form"):
        source = st.selectbox("Source", ["Salary", "Bonuses & Commissions", "Business Income", "Freelancing", "Consulting", "Dividends", "Royalties", "Other"])
        value = st.number_input("Amount", min_value=0.0)
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "bi-Weekly", "Monthly", "Quarterly", "Half-Yearly", "Annual"])
        start_date = st.date_input("Start Date", min_value=date(1925, 1, 1), max_value=date(2100, 12, 31))
        end_date = st.date_input("End Date", min_value=date.today(), max_value=date(2100, 12, 31))
        growth_rate = st.number_input("Expected Annual Growth Rate (%)", min_value=0.0)

        # Submit button for the form
        submit = st.form_submit_button("Add Income")

    # Process form submission
    if submit:
        if source and value and frequency and start_date and end_date and growth_rate:
            if end_date >= start_date:
                add_income(username, source, value, frequency, start_date, end_date, growth_rate)
                st.success("Income added successfully!")
            else:
                st.error("End Date must be after Start Date.")

    # Fetch and display incomes from SQL database
    incomes = get_incomes(username)

    for income in incomes:
        income_id, source, value, frequency, start_date, end_date, growth_rate = income
        
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("❌", key=f"delete_{income_id}"):
                delete_income(username,income_id)
                st.rerun()

        with col2:
            st.write(f"**Source**: {source} - **Value**: {value} - **Frequency**: {frequency}")

