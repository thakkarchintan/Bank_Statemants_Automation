import streamlit as st
import pandas as pd
from datetime import date
from database import *
from utils import *

def investment_details():
    st.markdown("### Investments & Assets")
    st.write("Use this section to list down all assets & investments which may or may not be generating additional income.")

    # Ensure session state variables exist
    if "selected_profile" not in st.session_state or not st.session_state["selected_profile"]:
        st.session_state["selected_profile"] = "Default"

    if "username" not in st.session_state or not st.session_state["username"]:
        st.session_state["username"] = "Guest"

    username = st.session_state["username"]
    selected_profile = st.session_state["selected_profile"]

    # Debugging output
    st.write("DEBUG: Username:", username, "Selected Profile:", selected_profile)

    if not username or not selected_profile:
        st.error("❌ Error: Username or profile is missing.")
        return

    # Investment input form
    with st.form(key='investment_form'):
        Investment_Type = st.selectbox("Investment or Asset Type", 
                                ["Savings Account", "Fixed Deposits", "Government Bonds", "Corporate Bonds", 
                                "Mutual Funds", "ETFs", "Stocks", "Real Estate", "Gold", "Collectibles", 
                                "Private Equity", "Commodities", "Art & Antiques", "Hedge Funds", 
                                "Provident Fund (PF)", "Precious Metals (Silver, Platinum)", "Foreign Currency", 
                                "Annuities", "Life Insurance Policies", "Business Ownership", "Cash", 
                                "Cryptocurrency", "Other"], key="Investment_Type")
        Amount = st.number_input("Amount Invested or Asset Value", min_value=0.0, key="Amount")
        Start_Date = st.date_input("Start Date", min_value=date(1925, 1, 1), max_value=date(2100, 12, 31), key="Start_Date")
        End_Date = st.date_input("End Date", min_value=date.today(), max_value=date(2100, 12, 31), key="End_Date")        
        Rate_of_Return = st.number_input("Expected Annual Rate of Return (%)", min_value=0.0, key="Rate_of_Return")

        submit_investment = st.form_submit_button(label="Add Investment")
        
        if submit_investment:
            if Investment_Type and Amount and Start_Date and End_Date:
                add_investment(username, selected_profile, Investment_Type, Amount, Start_Date, End_Date, Rate_of_Return)
                st.success("✅ Investment added successfully!")

    # Fetch investments
    investments = get_investments(username, selected_profile)
    
    if not isinstance(investments, list):
        investments = []  # Ensure it's a list

    st.subheader("Investment List")
    if not investments:
        st.write("❌ No investment records found.")
    else:
        df = pd.DataFrame(investments, columns=["ID", "Investment Type", "Amount", "Start Date", "End Date", "Rate of Return"])
        df = format_date_columns(df, ["Start Date", "End Date"])  # Format date columns
        display_added_data(df, "Investments")  # ✅ Fixed function call

