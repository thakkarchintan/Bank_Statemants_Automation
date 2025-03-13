import streamlit as st
from datetime import date
from database import *
import time
from utils import *
import uuid  
def expense_details() :
    st.header("Expenses")
    st.markdown("Use this section to list down all current and foreseeable future expenses. The more detailed you can be, the better the outcome will be.")
    username = st.session_state.get("username") 
    # Expense input form
    with st.form(key='expense_form'):
        exp_type = st.selectbox("Expense Type", ["Rent", "Household expenses", "Home Maintenance & Utilities", "Groceries", "Housekeeping Services",
                                                "School Tuition Fees", "College Tuition Fees", "Vacation - Domestic", "Vacation - International", 
                                                "EMI - Home Loan", "EMI - Auto Loan", "EMI - Education Loan", "EMI - Personal Loan", "EMI - Other Loan",
                                                "Health Insurance", "Life Insurance", "Auto Insurance", "Medical Expenses", "Marriage Expenses",
                                                "Fuel / Transportation", "Entertainment", "Dining Out", 
                                                "Subscriptions", "Personal Care", "Clothing", "Gifts", "Pet Care", 
                                                "Childcare", "Fitness & Gym", "Education (Courses, Books)", 
                                                "Charity & Donations", "Professional Services", "Hobbies & Leisure",
                                                "Other"], key="exp_type")
        exp_value = st.number_input("Amount", min_value=0.0, key="exp_value")
        exp_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "bi-Weekly", "Monthly", "Quarterly", 
                                                "Half-Yearly", "Annual"], key="exp_frequency")
        exp_start_date = st.date_input("Start Date", min_value=date(1925, 1, 1), max_value=date(2100, 12, 31), 
                                    key="exp_start_date")
        exp_end_date = st.date_input("End Date", min_value=date.today(), max_value=date(2100, 12, 31), 
                                    key="exp_end_date")
        inflation_rate = st.number_input("Expected Annual Inflation Rate (%)", min_value=0.0, key="inflation_rate")

        submit_expense = st.form_submit_button(label="Add Expense")

    if submit_expense:
        if exp_type and exp_value and exp_frequency and exp_start_date and exp_end_date and inflation_rate:
            if exp_end_date >= exp_start_date:
                add_expense(username, exp_type, exp_value, exp_frequency, exp_start_date, exp_end_date, inflation_rate)
        
                st.success("Expense added successfully and saved to your profile!")
            else:
                st.error("End Date must be after Start Date.")
                    
    expenses = get_expenses(username)
    df = pd.DataFrame(expenses)
    if not expenses:
        st.write("No expenses found.")
    else:
        df.columns = ["Expense_ID", "Expense_Type", "Value", "Frequency", "Start_Date","End_Date", "Inflation_Rate"]
        df.columns = df.columns.astype(str) 
        print(f"Expense Dataframe :{df}")
        df = format_date_columns(df,["Start_Date","End_Date"])
        st.subheader("Expense List")
        display_added_data(df,"Expenses")

        # Ask for savings rate
    with st.form(key='savings_rate_form'):    
        st.header("Savings Rate")
        st.markdown("This is the annual growth rate which will be applied to Annual Income - Annual Expenses")
        savings_rate = st.number_input("Savings Rate (%)", min_value=0.0, key="savings_rate")
        submit_saving_rate = st.form_submit_button("Add Saving Rate")

    if submit_saving_rate:
        if not savings_rate:
            add_savings(username, 0.0)
        if savings_rate:
            add_savings(username, savings_rate)
            st.success("Savings rate added successfully!")

    savings = get_savings(username)        

# Retrieve the fields for each document and display with an X button
    for saving in savings:
        Saving_ID , Saving_Rate = saving
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("❌", key=f"delete_savings_{Saving_ID}"):
                delete_savings(username,Saving_ID)
                st.rerun()
        with col2:
                st.write(f"**Saving**: {Saving_Rate}")