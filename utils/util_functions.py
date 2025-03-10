import streamlit as st
import pandas as pd
import plotly.express as px
import pdfplumber
import datetime as dt
import xlrd
from io import BytesIO
import os
import base64
import streamlit.components.v1 as components
import re
import uuid
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from database import *


# Function to categorize each row based on narration content
def categorize(narration,categorization_dict):
    for key in categorization_dict.keys():
        if key.lower() in str(narration).lower():
            return categorization_dict[key]
    return ""

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

def csv_to_df(uploaded_file,required_columns):
    # Find the header row by checking if all required columns are in the line
    header_row_index = None
    for i, line in enumerate(uploaded_file):
        # Decode bytes to string and process the line
        line = line.decode("utf-8").strip()
        line_columns = [col.strip('"') for col in line.split(",")]
        if set(required_columns).issubset(line_columns):  # Check if subset
            header_row_index = i
            break

    df = pd.DataFrame()

    if header_row_index is not None:
        # Reset file pointer and read the CSV with the identified header row
        uploaded_file.seek(0)  # Reset file pointer to the start
        df = pd.read_csv(uploaded_file, skiprows=header_row_index, header=0)
        
    return df

def pdf_to_df(uploaded_file,table_columns_pdf,bank):
    combined_df = pd.DataFrame()

    # Open the uploaded PDF file
    with pdfplumber.open(uploaded_file) as pdf:
        found_col=False
        all_col=[]
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                # Append the table data to the combined DataFrame
                for t in table:
                    # print(t)
                    if  not t[0]:
                        continue
                    if found_col and len(all_col)==len(t):
                        # print("\nkfkdhf\n")
                        combined_df.loc[len(combined_df)] = t
                        
                    elif set(table_columns_pdf).issubset(t):
                        found_col=True
                        all_col=t
                        # Convert the table to a DataFrame
                        combined_df = pd.DataFrame(columns=all_col)  
            
            # print(combined_df)
            if bank=="Kotak Bank" and i==0:
                combined_df = combined_df.drop(combined_df.columns[[1, 7]], axis=1)
                all_col=combined_df.columns
                # combined_df = combined_df.drop(0)

    # print(combined_df)
    return combined_df

def xls_to_df(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='xlrd')
    return df

def xlsx_to_df(uploaded_file):
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    return df

from utils import banks_date_format,table_columns_dic,table_columns_pdf_dic ,bank_status_dict
from database import get_categories

def format_uploaded_file(uploaded_file, bank, db_name, user_name):
    date_format=banks_date_format[bank]
    table_columns=table_columns_dic[bank]
    table_columns_pdf=table_columns_pdf_dic[bank]
    new_table_columns = ['Date','Narration','Debit','Credit','Balance']
    isCrDr=bank_status_dict[bank]
    df = pd.DataFrame()
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            df = csv_to_df(uploaded_file,table_columns)
        elif uploaded_file.name.lower().endswith('.xls'):
            df = xls_to_df(uploaded_file)
        elif uploaded_file.name.lower().endswith('.xlsx'):
            df = xlsx_to_df(uploaded_file)
        elif uploaded_file.name.lower().endswith('.pdf'):
            table_columns=table_columns_pdf
            df = pdf_to_df(uploaded_file,table_columns,bank)
        else:
            print("Unsupported file format")
        # print(df)
        # Find the start of the transaction table
        header_index = None
        all_table_columns=[]

        if set(table_columns).issubset(df.columns):
            all_table_columns=df.columns
        else: 
            for i, row in df.iterrows():
                if set(table_columns).issubset(row.values):  # Check if row contains all table columns
                    header_index = i
                    all_table_columns=row.values
                    break

        # If header_index is found, reformat the DataFrame from that row
        if header_index is not None:
            df = df.iloc[header_index + 1:]  # Skip to the row after the header
            df.columns = all_table_columns

        # Retain only the specified columns
        df = df[table_columns]
        
        for i in range(2):
            df = df.rename(columns={table_columns[i]:new_table_columns[i]})
        df = df.rename(columns={table_columns[4]:new_table_columns[4]})

        # print(df.dtypes)

        df['Date'] = df['Date'].astype(str)

        df['Date'] = df['Date'].str.replace(',', '/')
        
        # Convert the Date column to datetime and then format it
        if date_format is not None:
            df['Date'] = pd.to_datetime(df['Date'],format=date_format,errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            df['Date'] = pd.to_datetime(df['Date'],errors='coerce').dt.strftime('%Y-%m-%d')

        # Remove irrelevant data at the bottom
        # Assuming valid transaction rows should not have NaN in all key columns
        df = df.dropna(subset=['Date'], how="all").reset_index(drop=True)
        df = df.dropna(subset=['Narration'], how="all").reset_index(drop=True)
        # print(df)
        if isCrDr:
            # if bank == 'Kotak Bank':
            #     df['Credit'] = df[table_columns[3]].apply(lambda x: x if x > 0 else 0)
            #     df['Debit'] = df[table_columns[3]].apply(lambda x: -x if x < 0 else 0)
                
            # else:
            # Create separate credit and debit columns 
            df['Credit'] = df[table_columns[2]].where(df[table_columns[3]].str.contains(r'[cC]', na=False), 0)
            df['Debit'] = df[table_columns[2]].where(df[table_columns[3]].str.contains(r'[dD]', na=False), 0)


        else:
            for i in range(len(table_columns)):
                df = df.rename(columns={table_columns[i]:new_table_columns[i]})
        
        df = df[new_table_columns]

        # Convert 'Debit' and 'Credit' columns to numeric types for calculations
        
        df['Debit'] = df['Debit'].astype(str).str.replace(r'[^0-9.]', '', regex=True)
        df['Credit'] = df['Credit'].astype(str).str.replace(r'[^0-9.]', '', regex=True)
        df['Balance'] = df['Balance'].astype(str).str.replace(r'[^0-9.]', '', regex=True)
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce')
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce')
        # print(df)
        # Add a new column 'Category'
        df['Category'] = ""

        category_table="Categories"
        categorization_df=get_categories(category_table)
        debit_categorization_df = categorization_df[categorization_df['Type'] == 'Debit']
        credit_categorization_df = categorization_df[categorization_df['Type'] == 'Credit']

        credit_categorization_dict = dict(zip(credit_categorization_df['Keyword'], credit_categorization_df['Category']))
        debit_categorization_dict = dict(zip(debit_categorization_df['Keyword'], debit_categorization_df['Category']))
        
        df['Category'] = df.apply(
            lambda row: categorize(row['Narration'],credit_categorization_dict) if pd.notna(row['Credit']) and row['Credit'] != "" and row['Category']=="" else row['Category'],
            axis=1
        )

        df['Category'] = df.apply(
            lambda row: categorize(row['Narration'],debit_categorization_dict) if pd.notna(row['Debit']) and row['Debit'] != ""  and row['Category']=="" else row['Category'],
            axis=1
        )

        df.fillna(0, inplace=True)        

        return df
    
    except Exception as e:
        print(f"Error cleaning Excel file: {e}")
    return pd.DataFrame()
   
def display_data(df,Height,download_df=[],summary=False,db_name="",user_name="",category_present=False,category_list=[]):
    bal_df=pd.DataFrame()
    if category_present:
        bal_df=df[["Balance"]].copy()
        df.drop('Balance', axis=1, inplace=True)
        # print(bal_df)
    # print(df)
    # Configure the ag-Grid options without pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_side_bar()  # Add a sidebar
    if category_present:
        gb.configure_column("Category", editable=True, cellEditor="agSelectCellEditor", cellEditorParams={"values": category_list})

    # Automatically configure columns to fit content dynamically
    for column in df.columns:
        gb.configure_column(column, minWidth=100,wrapText=True)

    gb.configure_grid_options(enableColumnResizing=True, enableHorizontalScroll=True)

    gridOptions = gb.build()

    # Display the grid
    grid_response=AgGrid(df, gridOptions=gridOptions,enable_enterprise_modules=True,height=Height,update_mode=GridUpdateMode.MANUAL,use_container_width=True) 
    if not summary:
        with st.container():
            col1,col2 ,_,col4,col5,col6,col7 = st.columns([2,2,1,1,1,1,1])
            with col1:
                if category_present:
                    if st.button("Save Changes",use_container_width=True):
                        if grid_response["data"] is not None:
                            g_resonse=pd.DataFrame(grid_response["data"])
                            g_resonse = g_resonse.reset_index(drop=True)
                            bal_df = bal_df.reset_index(drop=True)
                            # print(g_resonse)
                            # print(bal_df)
                            updated_df = pd.concat([g_resonse, bal_df], axis=1)
                            # print(updated_df)
                            updated_df['Date'] = pd.to_datetime(updated_df['Date'],errors='coerce').dt.strftime('%Y-%m-%d')
                            delete_data(db_name,user_name,"1=1")
                            add_data(updated_df,False,db_name,user_name)
                            st.toast(":green[Data saved successfully.]")
            with col2:
                st.download_button(
                    key='dbs',
                    label="Download data",
                    data=convert_df_to_excel(download_df),
                    file_name="bank_statement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

def show_message(page):
    if page == "policies":
        refund_policy()
    else:
        home_page()

def display_graph(df,selected_name,selected_bank):
    # Extract month and year separately in the format "Jan 2024"
    df["month_year"] = df["Date"].dt.strftime("%b %Y")  # "Jan 2024" format
    # Create a sorting column for proper month-year order
    df["sort_order"] = df["Date"].dt.to_period("M")
    # Filter data for the selected name and bank
    if selected_bank!='All':
        df = df[df["Bank"] == selected_bank]
    if selected_name!='All':
        df = df[df["Name"] == selected_name]

    # Group by month and sum values, then sort
    monthly_data = (
        df.groupby(["month_year", "sort_order"])[["Debit", "Credit"]]
        .sum()
        .reset_index()
        .sort_values(by="sort_order")
    )

    # Drop the sorting column
    monthly_data = monthly_data.drop(columns=["sort_order"])

    custom_colors={"Debit":"#F08080", "Credit":"#5CB85C"}

    # Plot using Plotly
    fig = px.bar(
        monthly_data,
        x="month_year",
        y=["Debit", "Credit"],
        title=f"{selected_name if selected_name!='All'else ''} {'('+selected_bank+') ' if selected_bank!='All'else ''}{':'if selected_bank!='All' or selected_name!='All' else ''} Monthly Debit & Credit",
        labels={"month_year": "Month", "value": "Amount","variable":""},
        barmode="group",
        color_discrete_map=custom_colors
    )
    

    # Show figure in Streamlit
    st.plotly_chart(fig)

def display_graph1(df,selected_name,selected_bank,keyword,graph_name,debit_or_credit='all'):
    # Extract month and year separately in the format "Jan 2024"
    df["month_year"] = df["Date"].dt.strftime("%b %Y")  # "Jan 2024" format
    # Create a sorting column for proper month-year order
    df["sort_order"] = df["Date"].dt.to_period("M")
    # Filter data for the selected name and bank
    if selected_bank!='All':
        df = df[df["Bank"] == selected_bank]
    if selected_name!='All':
        df = df[df["Name"] == selected_name]
    
    df = df[df['Narration'].str.contains(keyword, case=False, na=False)]

    if df.empty:
        st.write("No data found.")
        return

    custom_colors={"Debit":"#F08080", "Credit":"#5CB85C"}
    lst=["Debit", "Credit"]

    if debit_or_credit=='Debit':
        custom_colors={"Debit":"#F08080"}
        lst=["Debit"]

    elif debit_or_credit=='Credit':
        custom_colors={"Credit":"#5CB85C"}
        lst=["Credit"]


    # Group by month and sum values, then sort
    monthly_data = (
        df.groupby(["month_year", "sort_order"])[lst]
        .sum()
        .reset_index()
        .sort_values(by="sort_order")
    )

    # Drop the sorting column
    monthly_data = monthly_data.drop(columns=["sort_order"])
    
    # Plot using Plotly
    fig = px.bar(
        monthly_data,
        x="month_year",
        y=lst,
        title=f"{selected_name if selected_name!='All'else ''} {'('+selected_bank+') ' if selected_bank!='All'else ''}{':'if selected_bank!='All' or selected_name!='All' else ''} {graph_name}",
        labels={"month_year": "Month", "value": "Amount","variable":""},
        barmode="group",
        color_discrete_map=custom_colors
    )

    # Show figure in Streamlit
    st.plotly_chart(fig)

def display_graph2(df,selected_name,selected_bank,is_low,graph_name):
    # Extract month and year separately in the format "Jan 2024"
    df["month_year"] = df["Date"].dt.strftime("%b %Y")  # "Jan 2024" format
    # Create a sorting column for proper month-year order
    df["sort_order"] = df["Date"].dt.to_period("M")
    # Filter data for the selected name and bank
    if selected_bank!='All':
        df = df[df["Bank"] == selected_bank]
    if selected_name!='All':
        df = df[df["Name"] == selected_name]
    
    if is_low:
        df = df[(df['Debit'] >= 0) & (df['Debit'] <= 500)]
    else:
        df = df[(df['Debit'] > 500) & (df['Debit'] <= 1500)]

    if df.empty:
        st.write("No data found.")
        return

    custom_colors={"Debit":"#F08080"}
    lst=["Debit"]

    # Group by month and sum values, then sort
    monthly_data = (
        df.groupby(["month_year", "sort_order"])[lst]
        .sum()
        .reset_index()
        .sort_values(by="sort_order")
    )

    # Drop the sorting column
    monthly_data = monthly_data.drop(columns=["sort_order"])
    
    # Plot using Plotly
    fig = px.bar(
        monthly_data,
        x="month_year",
        y=lst,
        title=f"{selected_name if selected_name!='All'else ''} {'('+selected_bank+') ' if selected_bank!='All'else ''}{':'if selected_bank!='All' or selected_name!='All' else ''} {graph_name}",
        labels={"month_year": "Month", "value": "Amount","variable":""},
        barmode="group",
        color_discrete_map=custom_colors
    )

    # Show figure in Streamlit
    st.plotly_chart(fig)

def show_agreement():
    html_string = """
    <div class="cont">
        <h2>Your Data, Your Control - Our Commitment to Privacy & Security</h2>
        <div class="para bolda">Your Data is Yours - No Sharing, No Selling</div>
        <div class="para">We do not share or sell your data. It is only used within the app to organize and categorize your transactions.</div>
        <div class="para bolda">You Upload, We Process</div>
        <div class="para">You manually upload your bank statements, and we only process the data you provide—nothing more, nothing less.</div>
        <div class="para bolda">You Can Delete Your Data Anytime</div>
        <div class="para">Your data, your choice! You can delete your uploaded data anytime, and once deleted, it is gone forever.</div>
        <div class="para">By using this app, you agree to these practices.If you have any questions, feel free to reach out at <span class="email">bankstatementsautomation@gmail.com</span></div>
    </div>
    """

    css_string = """
    <style>
        .cont {
            margin: auto;
            margin-top: 0px;
            margin-bottom: 20px;
            width: 80%;
        }
        .para {
            font-size: 20px;
            margin-top: 8px;
            line-height: 1.2;
        }
        .bolda {
            font-weight: bold;
            line-height: 1.2;
        }
        .email {
            font-weight: bold;
            color: #0056b3;
        }
    </style>
    """
    st.markdown(css_string, unsafe_allow_html=True)
    st.markdown(html_string, unsafe_allow_html=True)

def has_common_rows(df1, df2, col=['Name','Bank','Date','Narration','Debit','Credit']):
    return pd.merge(df1, df2, on=col, how='inner')
     
def home_page():
    css = """
        <style>
            *{
                font-family:sans-serif;
            }
            .container {
                overflow-x:hidden;
                max-width:100vw;
                max-height:100%;
                display:flex;
                flex-direction:column;
                gap:2rem;
            }
            .text-section {
                max-width: 70%;
            }
           
            h1 {
                all: unset;
                font-size: 1.8rem !important;
                margin-bottom:1rem !important;
                font-weight: bold !important;
                color: black;
            }

            h2 {
                all: unset;
                font-size: 1.3rem !important;
                margin: 20px 0 !important;
                font-weight: bold !important;
                color: black;
            }
            .para{
                font-size: 1rem;
                margin-bottom:10px;
            }
            .bold {
                font-weight:bold;
            }
            .section-subheading{
                font-weight:bold;
            }
            
            .policy{
                margin-top:40px;
                font-size:1rem;
                display:flex;
                flex-direction:column;
                gap:10px;
                justify-content:center;
                align-items:start;
            }
            .profile-section{
                display:flex;
                gap:20px;
                width:70%;
                margin-bottom:20px;
                justify-content:start;
                align-items:center;
                margin-top:15px;
            }
            .profile-image img{
                border-radius:100%;
                width:400px;
                aspect-ratio: 1 / 1;        
            }
            .profile-text p{
                margin-top:5px;
                margin-bottom:5px;
                font-size:1rem;
            }
            .profile-info{
                margin-top:15px;
            }
            .profile-info p{
                margin-bottom:5px;
                font-size:1rem;
            }
            .bold-text{
                font-weight: bold;
            }
            #list_of_supported_banks {
            max-width: 60%;
            border-collapse: collapse; /* Ensures table borders collapse together */
            margin-top:30px;
        }
        
        .leftpad2{
            padding-left:3px
        }
        
        .para-section{
            margin-top:15px;
        }

        #list_of_supported_banks th, #list_of_supported_banks td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
            word-wrap: break-word; /* Prevents text overflow */
        }

        /* Left-align the first column */
        #list_of_supported_banks th:nth-child(1), #list_of_supported_banks td:nth-child(1) {
            text-align: left;
            width: 33%; /* First column takes 33% of width */
        }

        /* Center-align the second and third columns */
        #list_of_supported_banks th:nth-child(2), #list_of_supported_banks th:nth-child(3),
        #list_of_supported_banks td:nth-child(2), #list_of_supported_banks td:nth-child(3) {
            text-align: center; /* Center-align text in columns 2 and 3 */
            width: 33%; /* Distribute equal width for second and third columns */
        }

        /* Background color for cells containing 'Yes' */
        .yes {
            background-color: #5CB85C;
            color: white;
            text-align: center;
        }

        /* Background color for cells containing 'Work in progress' */
        .work-in-progress {
            background-color: #F08080;
            color: white;
            text-align: center;
        }
        
        .footer{
            width:100%;
            height:fit-content;
            text-align: center;
            font-size: 1rem;
            color: #777;
            text-align:center;
            margin-top:3rem;
        }

        /* Add a subtle hover effect for rows */
        #list_of_supported_banks tr:hover {
            background-color: #f1f1f1;
        }

        /* Responsive behavior */
        @media (max-width: 1110px) {

            #list_of_supported_banks {
                font-size: 12px;
                max-width:100%;
            }

            #list_of_supported_banks th, #list_of_supported_banks td {
                padding: 8px;
            }
        }
        @media (max-width: 768px) {
            .text-section {
                max-width:100%
            }
            .profile-section {
                width:100%
            }
        } 
        </style>
        """
        
    html = f"""
        <div class="container">
                <div class="text-section">
                    <h1>Fintellect: Your All-in-One Financial Companion</h1>
                    <div class="para-section">
                        <div class="para">Take control of your finances with <span class="bold">Fintellect</span> , a powerful platform designed to:</div>
                        <div class="para"><span class="bold">✅ Assess & Project Your Net Worth – </span> Understand your financial standing today and plan for tomorrow.</div>
                        <div class="para"><span class="bold">✅ Organize & Analyse Your Bank Transactions – </span>Get a single, clear view of your spending across all accounts.</div>
                        <div class="para">Whether you’re tracking <span class="bold"> income, expenses, investments, or bank transactions, </span>  Fintellect helps you make informed financial decisions - effortlessly.</div>
                    </div>
                </div>  
                <div class = "profile">
                    <h1>📊 Track & Project Your Net Worth</h1>
                        <div class = "profile-section">
                            <div class = "profile-text">
                                <div class="para">Fintellect provides a <span class="bold">comprehensive overview of your financial status</span> by:</div>
                                <div class="para">🔹 <span class="bold">Calculating your current net worth</span> based on income, expenses, savings, and investments.</div>
                                <div class="para">🔹 <span class="bold">Projecting your future financial growth</span> using potential income and expense trends.</div>
                                <div class="para">🔹 <span class="bold">Helping you plan for major life goals</span> with financial forecasting tools.</div>
                                <div class="para">🔹 <span class="bold">Providing interactive graphs</span> to visualize your wealth accumulation over time.</div>
                            </div>
                        </div>
                </div>
                <div class = "profile">
                    <h1>💰 Organize & Categorize Your Transactions</h1>
                    <div class = "profile-section">
                        <div class = "profile-text">
                            <div class="para">Keeping track of <span class="bold">bank transactions</span> can be overwhelming, but Fintellect simplifies it:</div>
                            <div class="para">🔹 <span class="bold">Upload PDF/XLS bank statements</span> from multiple accounts.</div>
                            <div class="para">🔹 <span class="bold">Get a clean, structured view</span> of all transactions in one place.</div>
                            <div class="para">🔹 <span class="bold">Automatically categorize expenses</span> to identify spending patterns.</div>
                            <div class="para">🔹 <span class="bold">Gain powerful insights</span> into savings, subscriptions, and recurring charges.</div>
                        </div>
                    </div>
                </div>
        <div class="table-section">
            <h1>List of supported banks</h1>
            <table id="list_of_supported_banks">
                <tr>
                    <th>Name of the Bank</th>
                    <th>XLS or XLSX Supported</th>
                    <th>PDF Supported</th>
                </tr>
                <tr>
                    <td>Axis Bank</td>
                    <td class="yes">Yes</td>
                    <td class="yes">Yes</td>
                </tr>
                <tr>
                    <td>Bandhan Bank</td>
                    <td class="work-in-progress">Work in progress</td>
                    <td class="yes">Yes</td>
                </tr>
                <tr>
                    <td>Bank of India</td>
                    <td class="yes">Yes</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
                <tr>
                    <td>HDFC Bank</td>
                    <td class="yes">Yes</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
                <tr>
                    <td>ICICI Bank</td>
                    <td class="yes">Yes</td>
                    <td class="yes">Yes</td>
                </tr>
                <tr>
                    <td>Indian Bank</td>
                    <td class="work-in-progress">Work in progress</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
                <tr>
                    <td>Indian Overseas Bank</td>
                    <td class="yes">Yes</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
                <tr>
                    <td>Kotak Mahindra Bank</td>
                    <td class="work-in-progress">Work in progress</td>
                    <td class="yes">Yes</td>
                </tr>
                <tr>
                    <td>Punjab National Bank</td>
                    <td class="work-in-progress">Work in progress</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
                <tr>
                    <td>State Bank of India</td>
                    <td class="yes">Yes</td>
                    <td class="yes">Yes</td>
                </tr>
                <tr>
                    <td>Union Bank of India</td>
                    <td class="work-in-progress">Work in progress</td>
                    <td class="work-in-progress">Work in progress</td>
                </tr>
        </table>
    </div>
    <div class="profile">
        <h1>🔒 Privacy & Security Commitment</h1>
        <div class = "profile-section">
            <div class="profile-text">
                <div class="para">At Fintellect, we prioritize <span class="bold">your data privacy and security:</span></div>
                <div class="para"><span class="bold">✅  100% Encrypted & Secure – </span> Your data is protected with robust encryption methods.</div>
                <div class="para"><span class="bold">✅  No Data Sharing or Selling – </span> Your financial information stays with you.</div>
                <div class="para"><span class="bold">✅  You Upload, We Process – </span> The app processes only the data you provide - nothing more.</div>
                <div class="para"><span class="bold">✅  Delete Anytime – </span> Your data is yours. Once deleted, it’s gone forever</div>
            </div>
        </div>
    </div>
    <div class = "profile">
        <h1>📂 Easy Data Management & Export</h1>
        <div class = "profile-section">
            <div class = "profile-text">
                <div class="para">Need to keep financial records? Fintellect allows you to <span class="bold">export</span> your data to Excel for deeper analysis and record-keeping.</div>
            </div>
        </div>
    </div>
    <div class = "profile">
        <h1>Why Choose Fintellect?</h1>
        <div class = "profile-section">
            <div class = "profile-text">
                <div class="para">Managing finances shouldn’t feel like a chore. Fintellect is designed for <span class="bold">simplicity , automation , and clarity ,</span> helping you: </div>
                <div class="para">🔹 <span class="bold">Gain financial confidence</span> with structured insights.</div>
                <div class="para">🔹 <span class="bold"> Track, plan, and grow your wealth</span> with ease.</div>
                <div class="para">🔹 <span class="bold">Make informed decisions</span> with a clear view of your money.</div>
            </div>
        </div>
    </div>
    <div class = "profile">
        <h1>Disclaimer</h1>
        <div class = "profile-section">
            <div class = "profile-text">
                <div class="para">Fintellect provides financial insights based on user inputs but does <span class="bold">not offer financial advice</span>  We recommend consulting a professional for personalized guidance.</div>
                <div class="para">📩 Have questions? Reach out at <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a></div>
                <div class="para"><span class="bold">Start using Fintellect today and take control of your financial future! 🚀</span></div>
                <div class="para">Learn more about our <a href = "https://fintellect.co.in?page=policies"  target="_self"><span class = "bold" > Terms, Privacy & Security  Policies </span> </a></div>
            </div>
        </div>
    </div>
    <div class = "space-maker"></div>
    </div>
        """
        
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
       
def refund_policy():
    css = """
    <style>
        .container {
            overflow-x: hidden;
            min-width: 100vw;
            min-height: 100vh;
            background: white;
            box-sizing: border-box;
            padding: 20px;
            display:flex;
            flex-direction:column;
            gap:25px;
        }
        .policy-heading{
            margin-bottom:10px;
        }
        h1 {
                all: unset;
                font-size: 1.5rem !important;
                margin: 20px 0 !important;
                font-weight: bold !important;
                color: black;
            }

            h2 {
                all: unset;
                font-size: 1.3rem !important;
                margin: 20px 0 !important;
                font-weight: bold !important;
                color: black;
            }
            
        .center {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .sub-heading {
            height: 3%;
            font-size:1rem
        }
        ul {
            display: flex;
            flex-direction: column;
        }
        .footer {
            text-align: center;
            font-size: 1rem;
            color: #777;
        }
        .button {
            position: relative;
            top: 0px;
            left: 10px;
            padding: 10px 20px;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        .bold {
            font-weight: bold;
         }
        a{
            color: white;
        }
        p{
            width:60%;
        }
    </style>
    """
    html = f"""<body>
    <button class="button"><a href="https://fintellect.co.in/" target="_self">Home</a></button>
    <div class="container">
        <div>
            <h1>Fintellect Policies</h1>
            <div>
                <p><span class = "bold">Effective Date : </span>15-February-2025</p>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>1. Privacy Policy</h2>
            </div>
            <div class="policy">
                <h2>Introduction</h2>
                <p>At Fintellect, we recognize the importance of protecting your privacy and personal financial data. This Privacy Policy outlines the types of information we collect, how we use and safeguard that information, and your rights concerning your data.
                By accessing and using our services, you consent to the terms set forth in this policy.</p>
            </div>
            <div class="policy">
                <h2>Information We Collect</h2>
                <p>Fintellect provides financial tracking services, including Bank Statements Automation and Net Worth Projection.
                To enable these services, we may collect the following types of data:</p>
                <ul>
                    <li>Bank Transaction Data: Users may manually upload bank statements (PDF/XLS) for categorization and analysis.</li>
                    <li>Financial Planning Data: Users may input financial details to calculate and project their net worth.</li>
                    <li>User Identifiers: Basic profile information necessary for account management and security purposes.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>How We Use Your Information</h2>
                <p>The information you provide is used strictly for the purpose of delivering Fintellect's financial tracking and analysis functionalities. We do not sell, share, 
                or monetize user data. Our processing activities include:</p>
                <ul>
                    <li>Organizing and categorizing financial transactions for enhanced visibility.</li>
                    <li>Providing personalized financial insights through net worth calculations.</li>
                    <li>Enabling users to track their financial trajectory based on historical and projected data.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>Data Deletion & User Control</h2>
                <p>Users maintain full control over their data and may permanently delete their uploaded bank statements and net worth projections at any time. Upon deletion, 
                all associated data is irreversibly removed from our servers.</p>
            </div>
            <div class="policy">
                <h2>Data Security Measures</h2>
                <p>Fintellect employs AES-256 encryption for data storage and SSL/TLS encryption for all data transmissions. We implement industry-leading security 
                protocols to ensure the confidentiality and integrity of user data.</p>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>2. Terms & Conditions</h2>
            </div>
            <div class="policy">
                <h2>Acceptance of Terms</h2>
                <p>By accessing or using Fintellect, you agree to be bound by these Terms & Conditions. 
                If you do not agree with any provision herein, you must discontinue use of the platform.</p>
            </div>
            <div class="policy">
                <h2>Scope of Services</h2>
                <p>Fintellect provides a digital financial tracking solution comprising:</p>
                <ul>
                    <li>Bank Statements Automation: Users may upload and categorize bank transactions for financial analysis.</li>
                    <li>Net Worth Projection: Users may input financial information to generate future net worth forecasts.</li>
                </ul>
                <p>Fintellect is a financial data organization tool and does not provide investment advisory or financial planning services. Users should seek
                professional guidance for investment decisions.</p>
            </div>
            <div class="policy">
                <h2>Subscription & Payment Terms</h2>
                <p>Fintellect operates under a single subscription model, granting access to both Bank Statements Automation and Net Worth Projection features. Users may opt for a free
                version with limited access or upgrade to a paid subscription for enhanced capabilities.</p>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>3. Refund & Cancellation Policy</h2>
            </div>
            <div class="policy">
                <h2>Refund Eligibility</h2>
                <p>Refunds are applicable only for subscriptions and must be requested within 15 days of the initial purchase.
                Refund requests beyond this period will be reviewed on a case-by-case basis.</p>
            </div>
            <div class="policy">
                <h2>Cancellation of Subscription</h2>
                <p>Users may cancel their subscription at any time. Upon cancellation, all premium features will be immediately revoked, 
                and no further charges will apply in subsequent billing cycles</p>
            </div>
            <div class="policy">
                <h2>Processing Fees</h2>
                <p>Refunds may be subject to third-party processing 
                fees (e.g., Razorpay transaction fees), which are non-refundable.</p>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>4. Data Retention & Deletion Policy</h2>
            </div>
            <div class="policy">
                <h2>Data Storage and Retention</h2>
                <p>Fintellect retains user data solely for the purpose of delivering its financial tracking services. Users may access and manage their data at any time.</p>
            </div>
            <div class="policy">
                <h2>Permanent Deletion of User Data</h2>
                <ul>
                    <li>Users may initiate complete deletion of their data via the platform's settings.</li>
                    <li>Once deletion is confirmed, the data is permanently erased from Fintellect’s servers and cannot be recovered.</li>
                </ul>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>5. Security & Encryption Policy</h2>
            </div>
            <div class="policy">
                <h2>Security Protocols</h2>
                <p>Fintellect enforces a multi-layered security framework that includes:</p>
                <ul>
                    <li>AES-256 encryption for data at rest and SSL/TLS encryption for data in transit.</li>
                    <li>Strict access control policies ensuring that only authorized users can access their financial data.</li>
                    <li>Continuous security audits and monitoring to prevent unauthorized access</li>
                </ul>
            </div>
            <div class="policy">
                <h2>Third-Party Integrations</h2>
                <p>Currently, Fintellect operates as a standalone platform with no third-party financial service integrations. Future integrations, if any, will be disclosed transparently and subject to updated policy agreements.</p>
            </div>
        </div>
        <div class="policy-data">
            <div class="policy-heading">
                <h2>6. Governing Law & Legal Compliance</h2>
            </div>
            <div class="policy">
                <h2>Legal Disclaimer</h2>
                <p>Fintellect is not a regulated financial institution and does not provide any form of investment advisory, lending, or wealth management services. Users acknowledge that Fintellect is a financial data aggregation tool and must conduct independent due diligence before making financial decisions.</p>
            </div>
            <div class="policy">
                <h2>Jurisdiction & Dispute Resolution</h2>
                <p>These policies are governed by the laws of India. Any disputes arising from the use of Fintellect shall be subject to the exclusive jurisdiction of Indian courts.</p>
            </div>
        </div>
         <div>
            <h2>7. Contact Information</h2>
            <p>For inquiries related to these policies, please contact us at <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a></p>
        </div>
        <footer>Last Updated: 15-February-2025</footer>
    </div>
</body>"""
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)


def refresh_page():
    st.markdown('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)

def hide_3_dot_menu():
    st.markdown(
        """
        <style>
            [data-testid="stToolbar"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

def generate_username(email):
    prefix = email.split('@')[0]  # Get part before '@'
    cleaned_prefix = re.sub(r'[^a-zA-Z0-9]', '', prefix).lower()  # Remove special characters
    unique_suffix = str(uuid.uuid4())[:8]  # Generate a short unique identifier
    return f"{cleaned_prefix}_{unique_suffix}"

def display_aggrid(df, title):
    """Display a DataFrame using AG Grid with dynamic height based on the number of rows."""
    st.subheader(title)

    if df.empty:
        st.write("No data available.")
        return

    # Drop the "Id" column if it exists
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])

    # Determine grid height dynamically
    row_height = 35  # Approximate row height in pixels
    min_height = 200  # Minimum grid height
    max_height = 600  # Maximum grid height
    calculated_height = min(max_height, max(min_height, len(df) * row_height))

    # Configure AG Grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
    gb.configure_side_bar()  # Enable side bar
    gb.configure_default_column(editable=False, groupable=True)

    grid_options = gb.build()

    # Display AG Grid with dynamic height
    AgGrid(df, gridOptions=grid_options, height=calculated_height, fit_columns_on_grid_load=True, use_container_width=True)

def compute_annual_amount(value, frequency):
    frequencies = {
        'Daily': 365,
        'Weekly': 52,
        'bi-Weekly': 26,
        'Monthly': 12,
        'Quarterly': 4,
        'Half-Yearly': 2,
        'Annual': 1
    }
    return value * frequencies[frequency]

def apply_growth_rate(value, rate, years):
    return value * ((1 + rate / 100) ** years)

def format_date_columns(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
    return df