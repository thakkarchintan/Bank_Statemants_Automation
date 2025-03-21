import streamlit as st
from database import *
from utils import *
from tabs import *

def networth(authenticator):
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
    if "networth_confirm" not in st.session_state:
        st.session_state.networth_confirm = False
        
    def networth_confirm_submission():
        st.session_state.networth_confirm = True
        
    with st.sidebar:
        st.markdown("""
        <style>
            .st-emotion-cache-1gwvy71{
                padding-bottom:0rem;
            }
        </style>
    """, unsafe_allow_html=True)
        st.sidebar.markdown(
            """
            <div style="height: 350px;">
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with st.sidebar:
        st.sidebar.markdown("---")
        st.button("Delete all data", on_click=networth_confirm_submission,use_container_width=True)
        if st.session_state.networth_confirm:
            st.warning("Are you sure you want to delete all user data? This action is irreversible.")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Yes, Delete"):
                    drop_user_tables(username)
                    st.session_state.networth_confirm = False  # Reset confirmation state
                    st.rerun()
            with col2:
                if st.button("Cancel"):
                    st.session_state.networth_confirm = False  # Reset confirmation state
                    st.rerun()


    if st.sidebar.button("Log out",use_container_width=True):
        authenticator.logout()
    st.markdown(
                        """
                        <style>
                            div.block-container { padding-top: 0rem; } /* Reduce padding */
                            div[data-testid="stTabs"] { margin-top: -40px; } /* Move tabs higher */
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
    tabs = st.tabs(["Personal Profile", "Income Section", "Expenses Section", "Investments & Assets", "Summary & Networth"])
    with tabs[0]:
        personal_details()
    with tabs[1]:
        income_details()
    with tabs[2]:
        expense_details()
    with tabs[3]:
        investment_deatils()   
    with tabs[4]:
        result()