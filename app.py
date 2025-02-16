import streamlit as st
import razorpay
import streamlit.components.v1 as components
import pandas as pd
from io import BytesIO
from datetime import datetime , timedelta
import os
import time
from dotenv import load_dotenv

# Set Streamlit to wide mode
st.set_page_config(page_title="Bank Statements Automation",layout="wide")

from auth import Authenticator
from database import *
from utils import *

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
    dummy_data_file_path = os.path.join("assets","other","dummy_data.xlsx")
    dummy_data = pd.read_excel(dummy_data_file_path)
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
    
    uploaded_files = st.sidebar.file_uploader(f"Upload bank statement", type=["xls", "xlsx", "pdf"],accept_multiple_files=True)

    # Text input for account holder's name
    ac_name = st.sidebar.text_input("Account Holder's Name:", placeholder="Enter account holder's name here...")
    ac_name=ac_name.strip()

    override=False
    
    if st.sidebar.button("Add data"):
        # If a file is uploaded
        if uploaded_files:
            try:
                for uploaded_file in uploaded_files:
                    df=format_uploaded_file(uploaded_file,bank)
                    df = df[df['Narration'] != 'OPENINGBALANCE...']
                    # Default name if ac_name is not entered
                    if not ac_name:
                        ac_name=name
                    df['Name'] = ac_name

                    From=min(pd.to_datetime(df['Date'],errors='coerce'))
                    Till=max(pd.to_datetime(df['Date'],errors='coerce'))

                    # Add a new columna 'Bank' and 'Name'
                    df['Bank'] = bank

                    df = df[['Name','Bank','Date','Narration','Debit','Credit','Category']]

                    # get data from db
                    existing_df=get_transaction_data(db_name,user_name)
                    
                    # Ensure Date column is in the same format
                    df['Date'] = pd.to_datetime(df['Date'])
                    existing_df['Date'] = pd.to_datetime(existing_df['Date'])

                    # Ensure numeric columns have consistent types
                    df['Debit'] = df['Debit'].astype(float)
                    df['Credit'] = df['Credit'].astype(float)
                    existing_df['Debit'] = existing_df['Debit'].astype(float)
                    existing_df['Credit'] = existing_df['Credit'].astype(float)

                    # Strip whitespace and standardize text columns (optional)
                    text_cols = ['Name', 'Bank', 'Narration', 'Category']
                    for col in text_cols:
                        df[col] = df[col].str.strip()
                        existing_df[col] = existing_df[col].str.strip()

                    # Remove exact matches
                    df_filtered = df.merge(existing_df, on=df.columns.tolist(), how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)


                    no_of_transactions=df_filtered.shape[0]

                    if not df_filtered.empty:    
                        update_summary(db_name,summ_table,ac_name,bank,From,Till,no_of_transactions)

                        add_data(df_filtered,override,db_name,user_name)
                    st.toast(":green[Data updated successfully]")

            except Exception as e:
                print(f"Error in adding data: {e}")
                st.toast(":red[Something went wrong.]")
                st.toast(":red[Ensure that the uploaded bank statement matches the selected bank.]")

        else:
            # Display an error message if there is no data
            st.toast("Choose a Bank from the dropdown and upload the bank statement to get started.")

    # get data from db
    db_df=get_transaction_data(db_name,user_name)

    # Convert the Date column to datetime
    db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce')

    # Initialize session state for confirmation popup
    if "confirm" not in st.session_state:
        st.session_state.confirm = False

    def confirm_submission():
        st.session_state.confirm = True

    # Sidebar elements
    with st.sidebar:

        # Submit button inside sidebar
        st.button("Delete my data", on_click=confirm_submission)

        # Show confirmation inside sidebar
        if st.session_state.confirm:
            if not db_df.empty:
                st.warning("This will delete your all data and cannot be undone. Are you sure to proceed?")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Yes, Proceed"):
                        try:
                            delete_data(db_name,user_name,"1=1")
                            delete_data(db_name,summ_table,"1=1")
                            st.toast(":green[Data deleted successfully]")
                        except Exception as e:
                            print(f"Error in deleting: {e}")
                            st.toast(":red[Something went wrong.Please try again.]")
                        st.session_state.confirm = False
                        time.sleep(4)
                        st.rerun()
                        
                with col2:
                    if st.button("Cancel"):
                        st.session_state.confirm = False
                        st.rerun()
            else:
                st.toast(":red[There are no transactions in your account. No data to delete!]")

    # Create tabs
    tab1, tab2, tab3, tab4, tab5= st.tabs(["Dashboard", "Summary", "Bank Entries", "Feedback","Razorpay"])

    # Content for each tab
    with tab1:
        try :
            # show_messege()

            if not db_df.empty:
                name_options = ["All"] + list(db_df["Name"].unique())
                bank_options = ["All"] + list(db_df["Bank"].unique())

                g_df = db_df[['Date','Name','Bank','Debit','Credit']].copy()
                g1_df = db_df[['Date','Name','Bank','Narration','Debit','Credit']].copy()
                g2_df = db_df[['Date','Name','Bank','Narration','Debit','Credit']].copy()
                g3_df = db_df[['Date','Name','Bank','Debit']].copy()
                # Create 3 columns
                d1, d2, d3 = st.columns(3)

                # Dropdown to select a name and bank
                with d1:
                    selected_name = st.selectbox("Select Name:", options=name_options)

                with d2:
                    selected_bank = st.selectbox("Select Bank:", options=bank_options)

                show_data = False
                with d3:
                    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)  # Adds margin
                    if st.button("Show Data"):
                        show_data = True

                if show_data:
                    display_graph(g_df,selected_name,selected_bank)
                    display_graph1(g1_df,selected_name,selected_bank,'salary','Monthly Income from Salary','Credit')
                    display_graph1(g2_df,selected_name,selected_bank,'emi','Monthly EMI','Debit')
                    display_graph2(g2_df,selected_name,selected_bank,True,'Debit transactions between 0 to 500')
                    display_graph2(g2_df,selected_name,selected_bank,False,'Debit transactions between 501 to 1500')
        
            else:
                name_options = ["All"] + list(dummy_data["Name"].unique())
                bank_options = ["All"] + list(dummy_data["Bank"].unique())

                g_df = dummy_data[['Date','Name','Bank','Debit','Credit']].copy()
                g1_df = dummy_data[['Date','Name','Bank','Narration','Debit','Credit']].copy()
                g2_df = dummy_data[['Date','Name','Bank','Narration','Debit','Credit']].copy()
                g3_df = dummy_data[['Date','Name','Bank','Debit']].copy()
                # Create 3 columns
                d1, d2, d3 = st.columns(3)

                # Dropdown to select a name and bank
                with d1:
                    selected_name = st.selectbox("Select Name:", options=name_options)

                with d2:
                    selected_bank = st.selectbox("Select Bank:", options=bank_options)

                show_data = False
                with d3:
                    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)  # Adds margin
                    if st.button("Show Dummy Data",key='showd3'):
                        show_data = True

                if show_data:
                    display_graph(g_df,selected_name,selected_bank)
                    display_graph1(g1_df,selected_name,selected_bank,'salary','Monthly Income from Salary','Credit')
                    display_graph1(g2_df,selected_name,selected_bank,'emi','Monthly EMI','Debit')
                    display_graph2(g2_df,selected_name,selected_bank,True,'Debit transactions between 0 to 500')
                    display_graph2(g2_df,selected_name,selected_bank,False,'Debit transactions between 501 to 1500')
        
                  
        except Exception as e:
            print(f"Error in showing transction data graph: {e}")
            st.toast(":red[Something went wrong.]")

    with tab3:    
        try:
            if not db_df.empty:
                db_df['Date'] = db_df['Date'].dt.strftime('%d-%b-%Y')
                display_data(db_df,600)
                db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce')
                st.download_button(
                    key='dbb',
                    label="Download data",
                    data=convert_df_to_excel(db_df),
                    file_name="bank_statement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                if st.button("Show Dummy Data",key='showd2'):
                    dummy_data['Date'] = dummy_data['Date'].dt.strftime('%d-%b-%Y')
                    display_data(dummy_data,600)
                    dummy_data['Date'] = pd.to_datetime(dummy_data['Date'],errors='coerce')
                

        except Exception as e:
            print(f"Error in fetching transction data: {e}")
            st.toast(":red[Something went wrong.]")
    
    with tab2:
        try:
            if not db_df.empty:
                # st.subheader("Summary")
                summary_df=get_summary_data(db_name,summ_table)

                # Convert the Date column to datetime and then format it
                summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'],errors='coerce').dt.strftime('%d-%b-%Y')
                summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'],errors='coerce').dt.strftime('%d-%b-%Y')

                if not summary_df.empty:
                    display_data(summary_df,200)

                    # Convert the Date column to datetime and then format it
                    summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'],errors='coerce')
                    summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'],errors='coerce')

                    st.download_button(
                        key='dbs',
                        label="Download data",
                        data=convert_df_to_excel(summary_df),
                        file_name="bank_statement_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                if st.button("Show Dummy Summary",key='showd1'):
                    dummy_summary_data_file_path = os.path.join("assets","other","dummy_summary_data.xlsx")
                    dummy_summary_data=pd.read_excel(dummy_summary_data_file_path)
                    # Convert the Date column to datetime and then format it
                    dummy_summary_data['Start_Date'] = pd.to_datetime(dummy_summary_data['Start_Date'],errors='coerce').dt.strftime('%d-%b-%Y')
                    dummy_summary_data['End_Date'] = pd.to_datetime(dummy_summary_data['End_Date'],errors='coerce').dt.strftime('%d-%b-%Y')

                    display_data(dummy_summary_data,300)


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
        
        # File uploader (Optional)
        uploaded_file = st.file_uploader("Attach a file (optional)", type=["xls","xlsx","pdf", "png", "jpg"])

        # Submit button
        if st.button("Submit Feedback"):
            if feedback:  # Checking if input is not empty
                try:
                    data=(user_name,feedback)
                    add_feedback(db_name,feedback_table,data)
                    send_email(feedback,user_email,uploaded_file,ADMIN_EMAILS,SMTP_SERVER,SMTP_USER,SMTP_PASSWORD)
                    # send_email(feedback,user_email,ADMIN_EMAIL2,SMTP_SERVER,SMTP_USER,SMTP_PASSWORD)
                    st.toast(":green[Thank you for your feedback! It has been sent to the admin.]")
                except Exception as e:
                    print(f"Error sending feedback: {e}")
                    st.toast(":red[Failed to send feedback. Please try again later.]")
                
            else:
                st.warning("Please enter your feedback before submitting.")   

    with tab5:
        # Razorpay credentials
        RAZORPAY_KEY_ID = "rzp_test_oGlOoFOEoLSCxR"
        RAZORPAY_KEY_SECRET = "4vLa5BysJcGi4f6BWt1ptB5d"

        # Initialize the Razorpay client
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

        st.subheader("Razorpay Payment Gateway")

        # Get payment details from user
        amount_in_inr = st.number_input("Enter Amount (INR)", min_value=2500, step=100)
        email = st.text_input("Enter Email ID")
        contact = st.text_input("Enter Contact Number")

        if st.button("Proceed to Pay"):
            if amount_in_inr and email and contact:
                try:
                    # Create an order in Razorpay (amount in paise)
                    order_data = {
                        "amount": amount_in_inr * 100,  # convert INR to paise
                        "currency": "INR",
                        "payment_capture": 1,
                        "notes": {"email": email, "contact": contact}
                    }
                    order = client.order.create(data=order_data)
                    
                    # Prepare the Razorpay checkout widget as an HTML snippet
                    checkout_html = f"""
                    <html>
                    <head>
                        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
                    </head>
                    <body>
                        <script>
                        var options = {{
                            "key": "{RAZORPAY_KEY_ID}",
                            "amount": "{order['amount']}", // Amount is in paise
                            "currency": "INR",
                            "name": "Your Business Name",
                            "description": "Payment for Order",
                            "order_id": "{order['id']}",
                            "handler": function (response) {{
                                // You can handle the response here after successful payment
                                console.log(response);
                                window.location.href = "/?payment=success";
                            }},
                            "prefill": {{
                                "name": "{email}",
                                "email": "{email}",
                                "contact": "{contact}"
                            }},
                            "theme": {{
                                "color": "#F37254"
                            }}
                        }};
                        var rzp1 = new Razorpay(options);
                        rzp1.open();
                        </script>
                    </body>
                    </html>
                    """
                    # Render the checkout widget using Streamlit's components.
                    # height can be adjusted as needed.
                    components.html(checkout_html, height=600)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("Please enter all details before proceeding.")

else:
    auth_url=authenticator.login()  
    show_message(auth_url)