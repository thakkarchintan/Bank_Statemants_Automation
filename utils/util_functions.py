import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pdfplumber
import datetime as dt
import xlrd
from io import BytesIO
import os
import base64
import streamlit.components.v1 as components
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
    grid_response=AgGrid(df, gridOptions=gridOptions,enable_enterprise_modules=True,height=Height,use_container_width=True) 
    if not summary:
        with st.container():
            col1,col2 ,_,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
            with col1:
                if category_present:
                    if st.button("Save Changes"):
                        if grid_response["data"] is not None:
                            updated_df = pd.DataFrame(grid_response["data"])
                            print(updated_df)
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
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

def show_message(page):
    if page == "refund_policy":
        refund_policy()
    elif page == "privacy_policy":
        privacy_policy()
    elif page == "terms_condition":
        terms_condition()
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
        @media (max-width: 600px) {

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
                    <h1>Instantly Organize & Analyze Your Bank Transactions—All in One Place!</h1>
                    <div class="para-section">
                        <div class="para">Upload PDF or XLS bank statements from the <a href = "#list_of_supported_banks">list of supported banks</a> and instantly get a <span class = "bold">clean</span>, <span class = "bold">organized</span>, and <span class = "bold">standardized</span> view of all your transactions in one place.</div>
                        <div class="para bold">✅ Track Spending Patterns</div>
                        <div class="para bold">✅ Gain Intelligent Insights</div>
                    </div>
                </div>  
                <div class = "profile">
                <h1>Why I Created This App</h1>
                    <div class = "profile-section">
                    <div class = "profile-text">
                        <p>For <span class ="bold-text">3+ years</span>, I manually tracked my bank transactions—it was frustrating, inefficient, and time-consuming.
                        So, I built a tool to <span class ="bold-text">automate the entire process.</span></p>
                        <p>What started as a personal solution became something worth sharing. If you’ve ever struggled with organizing your finances, I hope this helps!.</p>
                        <div class = "profile-info">
                            <p class="bold"><a href="https://www.linkedin.com/in/1chintanthakkar/">Chintan Thakkar</a></p>
                        </div>     
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
        <div class = "policy">
                    <h1 class="section-heading">Commitment to Privacy & Security</h1>
                    <div>
                        <div>
                            <p><span class="section-subheading">🔒 100% Encrypted & Secure - </span>The data in this app is securely encrypted using robust encryption methods.</p>
                        </div>
                        <div>
                            <p><span class="section-subheading">📂 You Upload - The App processes - </span>The app only processes the data your provide - nothing more, nothing less.</p>
                        </div>
                        <div>
                            <p><span class="section-subheading ">🗑️ You Can Delete Your Data Anytime  - </span>Once deleted, it’s gone forever.</p>
                        </div>
                        <div>
                            <p><span class="section-subheading">🚫 No Sharing, No Selling - </span>Your data is yours. We do not and will not share or sell your data.</p>
                        </div>
                    </div>
                    <p>📩 Have questions? Reach out at  <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a></p>
                </div>
                <div class="para bold guidelines footer">
                    <a href="https://bankstatements.onrender.com/?page=privacy_policy" target="_self">Privacy Policy</a> , 
                    <a href="https://bankstatements.onrender.com/?page=refund_policy" target="_self">Refund Policy</a>
                    and <a href="https://bankstatements.onrender.com/?page=terms_condition" target="_self">Terms & Conditions</a>
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
        *{
            font-family:sans-serif;
        }
        .container {
            overflow-x: hidden;
            min-width: 100vw;
            min-height: 100vh;
            background: white;
            box-sizing: border-box;
            padding: 20px;
        }
        .policy p , .policy li {
            font-size: 1rem;
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
        .policy-data {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .sub-heading {
            height: 3%;
            font-size:1rem
        }
        ul {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .footer {
            text-align: center;
            font-size: 1rem;
            color: #777;
        }
        .button {
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 10px 20px;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        a{
            color: white;
        }
    </style>
    """
    html = f"""<body>
    <button class="button"><a href="https://bankstatements.onrender.com/" target="_self">Home</a></button>
    <div class="container">
        <h1 class="center top-heading">Fintellect Policies</h1>
        <div class="center sub-heading">
            <h2>Refund & Cancellation Policy</h2>
            <p><strong>Effective Date:</strong> 17-Feb-25</p>
            <p><strong>Legal Entity:</strong> Alpha Aces Advisory LLP</p>
        </div>
        <div class="policy-data">
            <div class="policy">
                <h2>1. General Refund Policy</h2>
                <p>At Fintellect, we prioritize customer satisfaction. Users can request refunds for subscriptions or one-time purchases—no questions asked.</p>
                <p>We offer a <strong>2-week trial period</strong> before requiring a purchase.</p>
                <p>Refunds are <strong>full refunds</strong>, excluding third-party processing fees.</p>
            </div>
            <div class="policy">
                <h2>2. Subscription Cancellations</h2>
                <ul>
                    <li>Users can cancel their subscriptions anytime.</li>
                    <li>Upon cancellation, <strong>access is revoked immediately</strong>.</li>
                    <li>If a user cancels after being charged, a full refund will be issued.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>3. One-Time Purchase Policy</h2>
                <ul>
                    <li>Users may request a refund for one-time purchases if dissatisfied.</li>
                    <li>Refund requests made in good faith will be honored.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>4. Payment Gateway & Processing Fees</h2>
                <ul>
                    <li>Refunds exclude <strong>third-party payment processing fees</strong>.</li>
                    <li>Refund timelines depend on the payment provider.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>5. Refund Request Process</h2>
                <p>Email <strong>support@fintellect.co.in</strong> for a refund request.</p>
                <p>Requests undergo <strong>manual review</strong> before processing.</p>
            </div>
            <div class="policy">
                <h2>6. Exceptional Cases</h2>
                <ul>
                    <li>No refunds for fraudulent or unauthorized transactions.</li>
                    <li>Fintellect may deny repeated refund requests.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>7. Governing Law & Dispute Resolution</h2>
                <p>Policy governed by <strong>Indian law</strong>.</p>
                <p>Refund disputes follow Indian legal procedures.</p>
            </div>
        </div>
        <div class="footer">
            <p>For queries, contact <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a>.</p>
            <p><strong>Last Updated:</strong> 17-Feb-25</p>
        </div>
    </div>
</body>"""
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
    
def privacy_policy():
# CSS for styling
 css = """
    <style>
        *{
            font-family:sans-serif;
        }
        .container {
            overflow-x: hidden;
            min-width: 100vw;
            min-height: 100vh;
            background: white;
            box-sizing: border-box;
            padding: 20px;
        }
        .policy p , .policy li {
            font-size: 1rem;
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
        .policy-data {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .sub-heading {
            height: 3%;
            font-size:1rem
        }
        ul {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .footer {
            text-align: center;
            font-size: 1rem;
            color: #777;
        }
        .button {
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 10px 20px;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        a{
            color: white;
        }
    </style>
    """
 html = f"""<body>
    <button class="button"><a href="https://bankstatements.onrender.com/" target="_self">Home</a></button>
    <div class="container">
        <h1 class="center top-heading">Fintellect Policies</h1>
        <div class="center sub-heading">   
            <h2>Privacy Policy</h2>
            <p><strong>Effective Date:</strong> 17-Feb-25</p>
            <p><strong>Legal Entity:</strong> Alpha Aces Advisory LLP</p>
        </div>
        <div class="policy-data">
            <div class="policy">
                <h2>1. Introduction</h2>
                <p>At Fintellect, we prioritize your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our application.</p>
            </div>
            <div class="policy">
                <h2>2. Data Collection & Processing</h2>
                <ul>
                    <li>We allow users to upload bank statements in PDF, Excel, and CSV formats.</li>
                    <li>All transaction data is stored on our fully encrypted cloud servers.</li>
                    <li>We do not use any third-party OCR tools, AI models, or APIs for data processing.</li>
                </ul>
            </div>
           <div class="policy">
                <h2>3. Data Security & Privacy</h2>
                <p>Your data is encrypted using AES-256 and SSL encryption.</p>
            </div>
            <div class="policy">
                <h2>4. User Rights & Data Control</h2>
                <p>Users can view, download, and delete their transaction data at any time.</p>
            </div>
              <div class="policy">
                <h2>5. Payment Processing</h2>
                <p>Payments will be processed through Razorpay.</p>
            </div>
            <div class="policy">
                <h2>6. Data Usage</h2>
                <p>We do not share or sell user data to third parties.</p>
            </div>
            <div class="policy">
                <h2>7. Changes to this Privacy Policy</h2>
                <p>We may update this policy from time to time. Users will be notified of significant changes.</p>
            </div>
        </div>
        <div class="policy-data acceptance">
            <h2>Acceptance of Terms</h2>
            <h2>By using Fintellect, you agree to these Terms & Conditions.</h2>
        <div class="policy">
                <h2>1. Usage Restrictions & Prohibited Activities</h2>
                <ul>
                    <li>Users must not engage in fraudulent or illegal activities.</li>
                    <li>The app is designed for personal use only.</li>
                </ul>
        </div>
        <div class="policy">
                <h2>2. Data Accuracy & Liability</h2>
                <p>Fintellect is an organizational tool, not financial advice.</p>
        </div>
        <div class="policy">
                <h2>3. Payments & Subscriptions</h2>
                <p>Future plans may include subscription-based and one-time payment options.</p>
        </div>
         <div class="policy">
                <h2>4. Termination & Data Deletion</h2>
                <p>Users can delete their accounts and all associated data permanently at any time.</p>
        </div>
        <div class="policy">
                <h2>5. Governing Law & Dispute Resolution</h2>
                <p>These Terms & Conditions shall be governed by the laws of India.</p>
        </div>
        </div>
        <div class="footer">
            <p>For queries, contact <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a>.</p>
            <p><strong>Last Updated:</strong> 17-Feb-25</p>
        </div>
    </div>
</body>"""
 st.markdown(css, unsafe_allow_html=True)
 st.markdown(html, unsafe_allow_html=True)
    
def terms_condition():
    css = """
    <style>
        *{
            font-family:sans-serif;
        }
        .container {
            overflow-x: hidden;
            min-width: 100vw;
            min-height: 100vh;
            background: white;
            box-sizing: border-box;
            padding: 20px;
        }
        .policy p , .policy li {
            font-size: 1rem;
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
        .policy-data {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .sub-heading {
            height: 3%;
            font-size:1rem
        }
        ul {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .footer {
            text-align: center;
            font-size: 1rem;
            color: #777;
        }
        .button {
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 10px 20px;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        a{
            color: white;
        }
    </style>
    """
    html = f"""
    <button class="button"><a href="https://bankstatements.onrender.com/" target="_self">Home</a></button>
    <div class = "container">
        <h1 class="center top-heading">Fintellect Policies</h1>
        <div class="center sub-heading">   
            <h2>Acceptance of Terms</h2>
            <p><strong>Effective Date:</strong> 17-Feb-25</p>
            <p><strong>Legal Entity:</strong> Alpha Aces Advisory LLP</p>
        </div>
        <div class="policy-data">
            <h2>By using Fintellect, you agree to these Terms & Conditions.</h2>
            <div class="policy">
                <h2>1. Usage Restrictions & Prohibited Activities</h2>
                <ul>
                    <li>Users must not engage in fraudulent or illegal activities.</li>
                    <li>The app is designed for personal use only.</li>
                </ul>
            </div>
            <div class="policy">
                <h2>2. Data Accuracy & Liability</h2>
                <p>Fintellect is an organizational tool, not financial advice.</p>
            </div>
            <div class="policy">
                <h2>3. Payments & Subscriptions</h2>
                <p>Future plans may include subscription-based and one-time payment options.</p>
            </div>
            <div class="policy">
                <h2>4. Termination & Data Deletion</h2>
                <p>Users can delete their accounts and all associated data permanently at any time.</p>
            </div>
            <div class="policy">
                <h2>5. Governing Law & Dispute Resolution</h2>
                <p>These Terms & Conditions shall be governed by the laws of India.</p>
            </div>
        </div>
        <div class="footer">
            <p>For queries, contact <a href="mailto:chintanthakkar@outlook.in">chintanthakkar@outlook.in</a>.</p>
            <p><strong>Last Updated:</strong> 17-Feb-25</p>
        </div>
    </div>
    """

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
