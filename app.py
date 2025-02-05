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
    db_df=pd.DataFrame()
    user_info=st.session_state['user_info']
    user_email = str(user_info.get('email'))
    user_name = user_email[:-10]
    user_name = user_name.replace('.','__')
    summ_table = user_name+'_summary'
    name=user_info.get('name')

    if name:
        user_data = (user_name,user_info.get('name'),user_email)
        add_user(db_name,'users',user_data)
    else:
        name=get_name(db_name,'users',user_name)


    if st.sidebar.button("Log out"):
        authenticator.logout()
        

    # sorting list of banks
    bank_list.sort()

    # Sidebar with bank selection dropdown and file upload
    bank = st.sidebar.selectbox("Select Bank", bank_list)
    
    uploaded_file = st.sidebar.file_uploader(f"Upload bank statement", type=["xls", "xlsx", "pdf"])

    # Text input for account holder's name
    ac_name = st.sidebar.text_input("Account Holder's Name:", placeholder="Enter account holder's name here...")
    ac_name=ac_name.strip()

    override=False

    
    if st.sidebar.button("Add data"):
        # If a file is uploaded
        if uploaded_file is not None:
            try:
                df=format_uploaded_file(uploaded_file,bank)
                
                # Default name if ac_name is not entered
                if not ac_name:
                    ac_name=name
                df['Name'] = ac_name

                From=min(pd.to_datetime(df['Date'],errors='coerce'))
                Till=max(pd.to_datetime(df['Date'],errors='coerce'))
                update_summary(db_name,summ_table,ac_name,bank,From,Till)
                
                # Add a new columna 'Bank' and 'Name'
                df['Bank'] = bank

                df = df[['Name','Bank','Date','Narration','Debit','Credit','Category']]
                # print(df)

                add_data(df,override,db_name,user_name)
                st.toast(":green[Data updated successfully]")

            except Exception as e:
                print(f"Error in adding data: {e}")
                st.toast(":red[Something went wrong.]")
                st.toast(":red[Ensure that the uploaded bank statement matches the selected bank.]")

        else:
            # Display an error message if there is no data
            st.toast("Choose a Bank from the dropdown and upload the bank statement to get started.")


    if st.sidebar.button("Delete my data"):
        try:
            delete_data(db_name,user_name,"1=1")
            delete_data(db_name,summ_table,"1=1")
            st.toast(":green[Data deleted successfully]")
        except Exception as e:
            print(f"Error in deleting: {e}")
            st.toast(":red[Something went wrong.]")
    
    # Create tabs
    tab1, tab2, tab3, tab4= st.tabs(["Dashboard", "Summary", "Bank Entries", "Feedback"])

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
        # show_messege()   

    with tab3:    
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
    
    with tab2:
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
    
    with tab4:
        # Admin Email Config
        ADMIN_EMAIL1 = os.getenv("ADMIN_EMAIL1")  
        ADMIN_EMAIL2 = os.getenv("ADMIN_EMAIL2")
        ADMIN_EMAILS=[ADMIN_EMAIL1,ADMIN_EMAIL2]

        SMTP_SERVER = os.getenv("SMTP_SERVER")

        SMTP_USER = os.getenv("SMTP_USER")  # Replace with your Gmail
        SMTP_PASSWORD = os.getenv("email_pass")  # Use an App Password, not your main password
        feedback_table='Feedback'
        st.subheader("User Feedback Form")

        # Text area for feedback
        feedback = st.text_area("Your Feedback:", placeholder="Write your feedback here...")
        feedback=feedback.strip()
        # Submit button
        if st.button("Submit Feedback"):
            if feedback:  # Checking if input is not empty
                try:
                    data=(user_name,feedback)
                    add_feedback(db_name,feedback_table,data)
                    send_email(feedback,user_email,ADMIN_EMAILS,SMTP_SERVER,SMTP_USER,SMTP_PASSWORD)
                    # send_email(feedback,user_email,ADMIN_EMAIL2,SMTP_SERVER,SMTP_USER,SMTP_PASSWORD)
                    st.toast(":green[Thank you for your feedback! It has been sent to the admin.]")
                except Exception as e:
                    print(f"Error sending feedback: {e}")
                    st.toast(":red[Failed to send feedback. Please try again later.]")
                
            else:
                st.warning("Please enter your feedback before submitting.")   
        
else:
    # st.header("Bank Statements Automation")
    auth_url=authenticator.login()  
    show_message(auth_url)