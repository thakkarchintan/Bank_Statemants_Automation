import streamlit as st
from common import authenticator
from database import *
from utils import *
from tabs import *

def networth():
    if "networth_confirm" not in st.session_state:
        st.session_state.networth_confirm = False
        
    def networth_confirm_submission():
        st.session_state.networth_confirm = True
        
    with st.sidebar:
        st.markdown("""
        <style>
            .st-emotion-cache-a6qe2i{
                padding-bottom:0rem;
            }
        </style>
    """, unsafe_allow_html=True)
        st.sidebar.markdown(
            """
            <div style="height: 300px;">
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with st.sidebar:
        st.sidebar.markdown("---")
        # Submit button inside sidebar
        # st.button("Delete my data", on_click=networth_confirm_submission,use_container_width=True)

    if st.sidebar.button("Log out",use_container_width=True):
        authenticator.logout()
        
        
    # Initialize session state if not already present
    if 'dependents' not in st.session_state:
        st.session_state.dependents = []
    create_database()
    create_user_table()
    if "user_info" in st.session_state:
        user_info = st.session_state["user_info"]
        email = user_info["email"]
    if not check_email_exists(email):
        username = generate_username(email)
        insert_user(email,username)
        st.session_state["username"] = username
    else :
        print(f"username fetched : {get_username(email)}")
        st.session_state["username"] = get_username(email)
        
    username = st.session_state.get("username") 
    create_dependents_table(username)
    create_expense_table(username)
    create_incomes_table(username)
    create_savings_table(username)
    create_investment_table(username)
    st.markdown(
                        """
                        <style>
                            div.block-container { padding-top: 0rem; } /* Reduce padding */
                            div[data-testid="stTabs"] { margin-top: -50px; } /* Move tabs higher */
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
    tabs = st.tabs(["Fintellect App ", "Personal Profile", "Income Section", "Expenses Section", "Investments & Assets", "Summary & Networth"])
    with tabs[0]:
        introduction()
    with tabs[1]:
        personal_details()
    with tabs[2]:
        income_details()
    with tabs[3]:
        expense_details()
    with tabs[4]:
            investment_deatils()   
    with tabs[5]:
        result()