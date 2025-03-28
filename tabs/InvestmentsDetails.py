import streamlit as st
from datetime import date
from database import *
import pandas as pd
from utils import *

@st.cache_data
def fetch_investments(username):
    return get_investments(username) or []

def investment_details():
    st.markdown("Use this section to list down all assets & investments which may or may not be generating additional income.")
    username = st.session_state.get("username")

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
            if End_Date >= Start_Date:
                add_investment(username, Investment_Type, Amount, Start_Date, End_Date, Rate_of_Return)
                st.success("Investment added successfully and saved to your profile!")
                st.session_state["updated"] = True
                st.rerun()
            else:
                st.error("End Date must be after Start Date.")

    # Fetch and display investments
    investments = fetch_investments(username)

    if investments:
        df = pd.DataFrame(investments, columns=["ID", "Investment Type", "Amount", "Start Date", "End Date", "Rate of Return"])
        df = format_date_columns(df, ["Start Date", "End Date"])  # Ensure date formatting
        st.subheader("Investment List")
        display_added_data(df, "Investments")
    else:
        st.write("No investment records found.")
