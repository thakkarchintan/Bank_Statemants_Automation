import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import xlrd  
import sys
import pdfplumber
from io import BytesIO
from datetime import datetime
import os
from dotenv import load_dotenv

from auth import Authenticator
from database import *
from utils import *
# from utils.bank_data import *

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

    if user_info.get('name'):
        st.write(f"Welcome ! {user_info.get('name')}")
        user_data = (user_info.get('id'),user_name,user_info.get('name'),user_info.get('email'))
        add_user(db_name,'users',user_data)


    if st.sidebar.button("Log out"):
        authenticator.logout()
        
    # sorting list of banks
    bank_list.sort()

    # Sidebar with bank selection dropdown and file upload
    bank = st.sidebar.selectbox("Select Bank", bank_list)

    # # Date Input
    # starting_date = st.sidebar.date_input("Select a starting date:")
    # ending_date = st.sidebar.date_input("Select a ending date:")

    # uploaded_file = st.sidebar.file_uploader(f"Upload your {bank} statement from {starting_date} to {ending_date}\nTransactions of other dates will be neglected", type=["xls", "xlsx", "csv","pdf"])
    uploaded_file = st.sidebar.file_uploader(f"Upload your {bank} statement", type=["xls", "xlsx", "csv","pdf"])

    # override = st.sidebar.selectbox(f"Want to override data :", ['No','Yes'])
    # override= True if override=='Yes' else False

    # st.sidebar.write(f"{'Data will be overridden' if override else 'data will be appended if not exists in table'}")
    override=False
    # Function to convert DataFrame to Excel
    def convert_df_to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        # Save the file
        writer.close()

        # Seek the buffer position to the start
        output.seek(0)
        
        return output

    date_format=banks_date_format[bank]

    if st.sidebar.button("Add data"):
        table_columns=table_columns_dic[bank]
        table_columns_pdf=table_columns_pdf_dic[bank]
        new_table_columns = ['Date','Narration','Debit','Credit']
        isCrDr=bank_status_dict[bank]

        # If a file is uploaded
        if uploaded_file is not None:

            df=format_uploaded_file(uploaded_file,table_columns,table_columns_pdf,new_table_columns,date_format,isCrDr)

            # Add a new column 'Category'
            df['Category'] = ""

            # Start - Load the categorization data from the Excel file to process and categorize the Debit transactions

            categorization_file_path = os.path.join("assets","other","categorization.xlsx")
            categorization_df = pd.read_excel(categorization_file_path, sheet_name='debit')

            # Create a dictionary for quick lookup
            categorization_dict = dict(zip(categorization_df['Narration Reference'], categorization_df['Category Reference']))

            # Function to categorize each row based on narration content
            def categorize_row(narration):
                for key in categorization_dict.keys():
                    if key.lower() in narration.lower():
                        return categorization_dict[key]
                return "Uncategorized"  # Default value if no match is found

            # Apply the categorization function to rows
            df['Category'] = df.apply(
                lambda row: categorize_row(row['Narration']) if pd.notna(row['Debit']) and row['Debit'] != "" else "",
                axis=1
            )

            # This will remove the text Uncategorized from the Category column where there was no match found
            # df['Category'] = df['Category'].replace('Uncategorized', '')

            # End - Load the categorization data from the Excel file to process and categorize the Debit transactions

            # Start - Load the categorization data from the Excel file for Credit transactions
            
            # Load the Credit categorization data from the Excel file
            credit_categorization_df = pd.read_excel(categorization_file_path, sheet_name='credit')

            # Create a dictionary for quick lookup
            credit_categorization_dict = dict(zip(credit_categorization_df['Narration Reference'], credit_categorization_df['Category Reference']))

            # Function to categorize each row based on narration content for Credit transactions
            def categorize_credit_row(narration):
                for key in credit_categorization_dict.keys():
                    if key.lower() in narration.lower():
                        return credit_categorization_dict[key]
                return "Uncategorized"  # Default value if no match is found

            # Apply the categorization function to rows
            df['Category'] = df.apply(
                lambda row: categorize_credit_row(row['Narration']) if pd.notna(row['Credit']) and row['Credit'] != "" else row['Category'],
                axis=1
            )

            # Remove the text Uncategorized from the Category column where there was no match found
            df['Category'] = df['Category'].replace('Uncategorized', '')

            # Add a new column 'Bank'
            df['Bank'] = bank

            df = df[['Bank','Date','Narration','Debit','Credit','Category']]
            df.fillna(0, inplace=True)
            # print(df)

            add_data(df,override,db_name,user_name)
            st.toast(":green[Data added successfully]")

            # End - Load the categorization data from the Excel file for Credit transactions

        else:
            # Display an error message if there is no data
            st.info("Choose a Bank from the dropdown and upload the bank statement to get started.")

    # get data from db
    df=get_data(db_name,user_name)

    # Convert the Date column to datetime and then format it
    df['Date'] = pd.to_datetime(df['Date'],errors='coerce').dt.strftime('%d-%b-%Y')

    # Show the data in an ag-Grid table
    st.subheader(f"Displaying Bank Statement data")

    # Configure the ag-Grid options without pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_side_bar()  # Add a sidebar
    
    # Automatically configure columns to fit content dynamically
    for column in df.columns:
        gb.configure_column(column, maxWidth=300,wrapText=True)

    gb.configure_grid_options(enableColumnResizing=True, enableHorizontalScroll=True)

    gridOptions = gb.build()

    # Display the grid
    AgGrid(df, gridOptions=gridOptions,enable_enterprise_modules=True)  # Adjust height as needed
    st.download_button(
        label="Download Excel file",
        data=convert_df_to_excel(df),
        file_name="bank_statement.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
else:
    st.markdown(
        """
        <style>
        .center {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top:150px;
        }
        </style>
        <div class="center">
            <h3>Bank Statements Automation</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    authenticator.login()
    
#     st.title("Bank Statements Automation")    