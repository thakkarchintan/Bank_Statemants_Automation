import streamlit as st
import pandas as pd
# import matplotlib.pyplot as plt
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pdfplumber
import datetime as dt
import xlrd
from io import BytesIO
import os
import base64

# Function to categorize each row based on narration content
def categorize(narration,categorization_dict):
    for key in categorization_dict.keys():
        if key.lower() in narration.lower():
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
from database import get_category_df

def format_uploaded_file(uploaded_file, bank, db_name, user_name):
    date_format=banks_date_format[bank]
    table_columns=table_columns_dic[bank]
    table_columns_pdf=table_columns_pdf_dic[bank]
    new_table_columns = ['Date','Narration','Debit','Credit']
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
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce')
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce')
        # print(df)
        # Add a new column 'Category'
        df['Category'] = ""

        category_table=user_name if user_name!='professionalbuzz' and user_name!='shirishkumar1949' else "categories"
        debit_categorization_df=get_category_df(db_name,category_table+"_debit")
        credit_categorization_df=get_category_df(db_name,category_table+"_credit")

        credit_categorization_dict = dict(zip(credit_categorization_df['keyword'], credit_categorization_df['category']))
        debit_categorization_dict = dict(zip(debit_categorization_df['keyword'], debit_categorization_df['category']))

        df['Category'] = df.apply(
            lambda row: categorize(row['Narration'],credit_categorization_dict) if pd.notna(row['Credit']) and row['Credit'] != "" else "",
            axis=1
        )

        df['Category'] = df.apply(
            lambda row: categorize(row['Narration'],debit_categorization_dict) if pd.notna(row['Debit']) and row['Debit'] != "" else row['Category'],
            axis=1
        )

        df.fillna(0, inplace=True)        

        return df
    
    except Exception as e:
        print(f"Error cleaning Excel file: {e}")
    return pd.DataFrame()
   
def display_data(df,Height):
    # Configure the ag-Grid options without pagination
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_side_bar()  # Add a sidebar
    
    # Automatically configure columns to fit content dynamically
    for column in df.columns:
        gb.configure_column(column, minWidth=100,wrapText=True)

    gb.configure_grid_options(enableColumnResizing=True, enableHorizontalScroll=True)

    gridOptions = gb.build()

    # Display the grid
    AgGrid(df, gridOptions=gridOptions,enable_enterprise_modules=True,height=Height)  

def show_message(url):
    def get_base64_image(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    image_base64 = get_base64_image("assets/homepage/profile_image.jpg")
    
    css = """
    <style>
        .container {
            width:100vw;
            height:100%;
            display:flex;
            flex-direction:column;
            gap:2rem;
        }
        .text-section {
            max-width: 90%;
        }
        .para{
            font-size: 1.2rem;
            margin-bottom:10px;
        }
        .section-heading{
            font-size:1.5rem;
        }
        
        .policy h2{
            font-size:1.5rem;
        }
        .policy p {
            font-size:1.2rem;
        }
        .policy{
            line-height:1;
        }
        .profile{
            margin-bottom:10px;
            margin-top:10px;
        }
        .gcenter {
            width: 100%;
            display: flex;
            margin-top: 10px;
        }
        .google-button {
            background-color: #4285F4;
            margin-right: 5px;
            color: white !important;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 1.5rem;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            text-decoration: none !important;
            gap:5px;
        }
        .google-button img {
            width: 1.5rem;
            height:1.5rem;
            margin-left: 5px;
            border-radius: 50%;
        }
        .profile-section{
            display:flex;
            gap:20px;
            width:90%;
            margin-top:20px;
            margin-bottom:20px;
            justify-content:start;
            align-items:center;
        }
        .profile-image img{
            border-radius:100%;
        }
        .profile-text p{
            margin-top:5px;
            margin-bottom:5px;
            font-size:1.2rem;
        }
        .profile-info{
            margin-top:15px;
        }
        .profile-info p{
            margin-top:5px;
            margin-bottom:5px;
            font-size:1.2rem;
        }
        .bold-text{
            font-weight: bold;
        }
         table {
            width: 60%;
            border-collapse: collapse;
            margin: 20px;
            font-family: Arial, sans-serif;
            text-align: center; /* Ensures all text in table is centered */
        }
        th, td {
            border: 1px solid black;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #f4f4f4;
            text-align: center;
        }
    
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .table-section h1{
            margin-left:20px;
        }
    </style>
    """
    
    html = f"""
    <div class="container">
            <div class="text-section">
                <h1 class="section-heading">All Your Bank Transactions. One Unified View.</h1>
                <div class="para">Upload PDF or XLS bank statements from the <a href = "#bank-table">list of supported banks</a> and instantly get a clean, organized, and standardized view of all your transactions in one place.</div>
                <div class="para">Gain powerful insights and analytics helping you see trends, hidden charges and other analytics from your transactions data never before!</div>
            </div>
            <div class = "policy">
                <h1 class="section-heading">Our Commitment to Privacy & Security</h1>
                <div>
                    <h2 class="section-subheading">100% Encrypted & Secure</h2>
                    <p>All the data is 100% encrypted using the most sophisticated encryption methods to ensure user privacy and security.</p>
                </div>
                <div>
                    <h2>You Upload, We Process</h2>
                    <p>You manually upload your bank statements, and we only process the data you provide - nothing more, nothing less.</p>
                </div>
                <div>
                    <h2>You Can Delete Your Data Anytime</h2>
                    <p>Your data, your choice! You can delete your uploaded data anytime, and once deleted, it is gone forever.</p>
                </div>
                    <div>
                    <h2>Your Data is Yours - No Sharing, No Selling</h2>
                    <p>We do not and will not share or sell your data. The data is used within the app to organize and categorize transactions.</p>
                </div>
                <p>If you have any questions, feel free to reach out at <a href="mailto:bankstatementsautomation@gmail.com">bankstatementsautomation@gmail.com</a></p>
            </div>
            <div class="gcenter">
                <a href="{url}" class="google-button" target="_self">
                    Login with Google
                    <img src="https://icon2.cleanpng.com/lnd/20241121/sc/bd7ce03eb1225083f951fc01171835.webp" alt="Google logo" />
                </a>
            </div>
            <div class = "profile">
             <h1>Why I Created This App</h1>
                <div class = "profile-section">
                <div class = "profile-image">
                    <img src="data:image/jpeg;base64,{image_base64}" width="200">
                </div>
                <div class = "profile-text">
                    <p>For over <span class ="bold-text">three years</span> , I manually categorized my bank transactions, trying to make sense of where my money was going. 
                    It was tedious, time-consuming, and honestly—inefficient.</p>
                    <p>At some point, I realized there had to be a <span class ="bold-text">better way</span>. So, I decided to <span class ="bold-text">automate the entire process</span>. What started as a personal tool quickly turned
                    into something I thought could benefit others too.</p>
                    <p>That’s why I’m sharing it with my network—if you’ve ever struggled with organizing your finances, 
                    I hope this helps! Would love to hear your thoughts. 🚀.</p>
                    <div class = "profile-info">
                        <p>Chintan Thakkar</p>
                        <p><a href="https://www.linkedin.com/in/1chintanthakkar/">Linkedin</a></p> 
                    </div>     
                </div>
            </div>
            </div>
    <diV class="table-section">
        <h1>List of supported banks</h1>
        <table id="bank-table">
            <tr>
                <th>Name of the Bank</th>
                <th>XLS or XLSX Supported</th>
                <th>PDF Supported</th>
            </tr>
            <tr>
                <td>Bank of India</td>
                <td>Yes</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>HDFC Bank</td>
                <td>Yes</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>Indian Overseas Bank</td>
                <td>Yes</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>Axis Bank</td>
                <td>Yes</td>
                <td>Yes</td>
            </tr>
            <tr>
                <td>ICICI Bank</td>
                <td>Yes</td>
                <td>Yes</td>
            </tr>
            <tr>
                <td>State Bank of India</td>
                <td>Yes</td>
                <td>Yes</td>
            </tr>
            <tr>
                <td>Bandhan Bank</td>
                <td>Work in progress</td>
                <td>Yes</td>
            </tr>
            <tr>
                <td>Indian Bank</td>
                <td>Work in progress</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>Kotak Mahindra Bank</td>
                <td>Work in progress</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>Punjab National Bank</td>
                <td>Work in progress</td>
                <td>Work in progress</td>
            </tr>
            <tr>
                <td>Union Bank of India</td>
                <td>Work in progress</td>
                <td>Work in progress</td>
            </tr>
        </table>
    </div>
<div class = "space-maker"></div>
</div>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)

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
        <h3>Your Data, Your Control - Our Commitment to Privacy & Security</h3>
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

def has_common_rows(df1, df2):
    common = pd.merge(df1, df2, how='inner')
    return not common.empty

