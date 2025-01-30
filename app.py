import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
from dotenv import load_dotenv

from auth import Authenticator
from database import *
from utils import *

# Set Streamlit to wide mode
st.set_page_config(page_title="Bank Statements Automation",layout="wide")

load_dotenv()

showToast=False

authenticator = Authenticator(
    token_key=os.getenv("TOKEN_KEY"),
    secret_path = "/etc/secrets/Bank_statement.json",
    redirect_uri="https://bankstatements.onrender.com",
)

authenticator.check_auth()


db_name=os.getenv("DATABASE")

if st.session_state["connected"]:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Bank Entries", "Summary"])
    db_df=pd.DataFrame()
    # Content for each tab
    with tab1:
        st.markdown(
            """
            <style>
            .center {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            </style>
            <div>
                <h3>Bank Statements Automation</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        user_info=st.session_state['user_info']
        user_name = str(user_info.get('email'))
        user_name = user_name[:-10]
        user_name = user_name.replace('.','__')
        summ_table = user_name+'_summary'

        if user_info.get('name'):
            user_data = (user_info.get('id'),user_name,user_info.get('name'),user_info.get('email'))
            add_user(db_name,'users',user_data)


        if st.sidebar.button("Log out"):
            authenticator.logout()
            
        # sorting list of banks
        bank_list.sort()

        # Sidebar with bank selection dropdown and file upload
        bank = st.sidebar.selectbox("Select Bank", bank_list)
        
        uploaded_file = st.sidebar.file_uploader(f"Upload your {bank} statement", type=["xls", "xlsx", "pdf"])

        # override = st.sidebar.selectbox(f"Want to override data :", ['No','Yes'])
        # override= True if override=='Yes' else False

        # st.sidebar.write(f"{'Data will be overridden' if override else 'data will be appended if not exists in table'}")
        override=False


        if st.sidebar.button("Add data"):

            # If a file is uploaded
            if uploaded_file is not None:
                try:
                    df=format_uploaded_file(uploaded_file,bank)

                    From=min(pd.to_datetime(df['Date'],errors='coerce'))
                    Till=max(pd.to_datetime(df['Date'],errors='coerce'))
                    update_summary(db_name,summ_table,bank,From,Till)
                    # Add a new column 'Bank'
                    df['Bank'] = bank

                    df = df[['Bank','Date','Narration','Debit','Credit','Category']]
                    # print(df)

                    add_data(df,override,db_name,user_name)
                    st.toast(":green[Data updated successfully]")

                except Exception as e:
                    print(f"Error in adding data: {e}")
                    st.toast(":red[Something went wrong.]")
                    st.toast("Choose a Bank from the dropdown and upload the bank statement of same bank to get started.")

            else:
                # Display an error message if there is no data
                st.toast("Choose a Bank from the dropdown and upload the bank statement of same bank to get started.")

        if st.sidebar.button("Delte all data"):
            try:
                delete_data(db_name,user_name,"1=1")
                delete_data(db_name,summ_table,"1=1")
                st.toast(":green[Data deleted successfully]")
            except Exception as e:
                print(f"Error in deleting: {e}")
                st.toast(":red[Something went wrong.]")

        show_messege(True)   


    with tab2:    
        try:
            # get data from db
            db_df=get_transaction_data(db_name,user_name)

            # Convert the Date column to datetime and then format it
            db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce').dt.strftime('%d-%b-%Y')

            if not db_df.empty:
                display_data(db_df,600)

                st.download_button(
                    key='dbb',
                    label="Download Excel file",
                    data=convert_df_to_excel(db_df),
                    file_name="bank_statement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            print(f"Error in fetching transction data: {e}")
            st.toast(":red[Something went wrong.]")
    
    with tab3:
        try:
            # st.subheader("Summary")
            summary_df=get_summary_data(db_name,summ_table)

            # Convert the Date column to datetime and then format it
            summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'],errors='coerce').dt.strftime('%d-%b-%Y')
            summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'],errors='coerce').dt.strftime('%d-%b-%Y')

            if not summary_df.empty:
                display_data(summary_df,200)

                st.download_button(
                    key='dbs',
                    label="Download Excel file",
                    data=convert_df_to_excel(summary_df),
                    file_name="bank_statement_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            # else:
            #     st.toast(":red[Please add data first.]")
        except Exception as e:
            print(f"Error in fetching summary data: {e}")
            st.toast(":red[Something went wrong.]")

        
    
    
else:
    # st.header("Bank Statements Automation")
    st.markdown(
        """
        <style>
        .center {
            display: flex;
            margin-top:0;
            justify-content: center;
            align-items: center;
        }
        </style>
        <div class="center">
            <h1>Bank Statements Automation</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    show_messege(False)
    
    authenticator.login()
    
#     st.title("Bank Statements Automation")   