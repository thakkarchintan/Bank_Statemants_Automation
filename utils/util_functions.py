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

# Function to categorize each row based on narration content
def categorize_debit_row(narration):
    for key in debit_categorization_dict.keys():
        if key.lower() in narration.lower():
            return debit_categorization_dict[key]
    return ""

def categorize_credit_row(narration):
    for key in credit_categorization_dict.keys():
        if key.lower() in narration.lower():
            return credit_categorization_dict[key]
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
            if bank=="Kotak Mahindra Bank" and i==0:
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

from utils import debit_categorization_dict,banks_date_format,table_columns_dic,table_columns_pdf_dic ,bank_status_dict, credit_categorization_dict

def format_uploaded_file(uploaded_file, bank):
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
        df['Date'] = pd.to_datetime(df['Date'],format=date_format,errors='coerce').dt.strftime('%Y-%m-%d')

        # Remove irrelevant data at the bottom
        # Assuming valid transaction rows should not have NaN in all key columns
        df = df.dropna(subset=['Date'], how="all").reset_index(drop=True)
        df = df.dropna(subset=['Narration'], how="all").reset_index(drop=True)
        # print(df)
        if isCrDr:
            # if bank == 'Kotak Mahindra Bank':
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

        df['Category'] = df.apply(
            lambda row: categorize_credit_row(row['Narration']) if pd.notna(row['Credit']) and row['Credit'] != "" else "",
            axis=1
        )

        df['Category'] = df.apply(
            lambda row: categorize_debit_row(row['Narration']) if pd.notna(row['Debit']) and row['Debit'] != "" else row['Category'],
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
    css = """
    <style>
        .container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 2.5%;
            max-width: 100%;
            margin: auto;
            margin-top: 0;
        }
        .video-section {
            flex: 1;
            max-width: 50%;
        }
        .text-section {
            flex: 1;
            max-width: 50%;
        }
        h2{
            margin-top:0;
            margin-bottom:0;
            padding-top:0;
            padding-bottom:0;
        }
        .para {
            font-size: 20px;
            margin-top: 10px;
            line-height: 1.3;
        }
        .note {
            margin-top: 15px;
            font-size: 20px;
            line-height: 1.3;
        }
        iframe {
            width: 100%;
            height: 290px;
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
            padding: 5px 10px;
            font-size: 17px;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            text-decoration: none !important;
        }
        .google-button img {
            width: 20px;
            margin-left: 5px;
            border-radius: 50%;
        }
    </style>
    """
    
    html = f"""
    <div class="container">
        <div class="video-section">
            <h3>Tutorial</h3>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/GcZW24SkbHM?si=hfxhPfJ6T2BakXNh" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
        <div class="text-section">
            <h3>All Your Bank Transactions. One Unified View.</h3>
            <div class="para">Tired of juggling multiple bank statements? Upload statements from any Indian bank and instantly get a clean, organized, and standardized view of all your transactions in one place.</div>
            <div class="para">Gain powerful insights into your income, expenses, and spending trends with smart analytics - helping you stay in control of your finances like never before.</div>
            <div class="note">Ps - The app is in its early development stage and we would welcome the opportunity to build it together with you.</div>
            <div class="gcenter">
                <a href="{url}" class="google-button" target="_self">
                    Login with Google
                    <img src="https://icon2.cleanpng.com/lnd/20241121/sc/bd7ce03eb1225083f951fc01171835.webp" alt="Google logo" />
                </a>
            </div>
        </div>
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