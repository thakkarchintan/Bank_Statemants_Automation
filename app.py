import streamlit as st
import os
st.set_page_config(page_title="Fintellect",page_icon=os.getenv("Fevicon_Path"),layout="wide")
import razorpay
import streamlit.components.v1 as components
import pandas as pd
import time
from database import *
from utils import *
from constant_variables import *
from streamlit_js_eval import streamlit_js_eval
from networth import *
from auth import Authenticator


if "connected" not in st.session_state:
    st.session_state["connected"] = False
    
if "login_message_shown" not in st.session_state:
    st.session_state["login_message_shown"] = False

st.markdown(
    """
    <style>
        /* Hide the three-dot menu */
        [data-testid="stToolbar"] {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        /* Remove top and bottom padding */
        .block-container {
            padding-bottom: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components

components.html(
    """
    <meta property="og:title" content="Fintellect" />
    <meta property="og:image" content="https://res.cloudinary.com/dwszdaeqw/image/upload/t_Fintellect/v1742560314/nubtvotgjgc2pc99azh9.png" />
    <meta property="og:url" content="https://fintellect.co.in" />
    """,
    height=0
)

query_params = st.query_params
page = query_params.get("page", ["home"]) 

authenticator = Authenticator(
    token_key=TOKEN_KEY,
    secret_path = SECRET_PATH,
    redirect_uri=REDIRECT_URI,
)

authenticator.check_auth()

db_name=DATABASE
# Define available finance-related apps
apps = {
    "🏦 Bank Statements Analyzer": "bank_statements",
    "📊 Net Worth Tracker": "networth",
    # "📜 eCAS Viewer": "ecas",
    # "📈 Stock Portfolio Manager": "stock_portfolio",
    # "💰 Crypto Insights": "crypto_insights",
    # "📉 Bond Analytics": "bond_analytics",
    # "🔍 Expense Tracker": "expense_tracker",
    # "📑 Tax Estimator": "tax_estimator",
    # "📊 Trading Performance Dashboard": "trading_performance",
}

if st.session_state["connected"]:
    user_info=st.session_state['user_info']
    name=user_info.get('name')
    if name:
        user_email=str(user_info.get('email'))
        streamlit_js_eval(js_expressions=f"localStorage.setItem('local_email', '{user_email}')", key="el")
        time.sleep(2)
    else :
        user_email = str(streamlit_js_eval(js_expressions="localStorage.getItem('local_email')", key="ef"))
        time.sleep(2)
        st.session_state['user_info']["email"]=user_email
    user_name = user_email[:-10]
    user_name = user_name.replace('.','__')
    summ_table = user_name+'_summary'
    if name:
        user_data = (user_name,user_info.get('name'),user_email)
        add_user(db_name,'users',user_data)
    else:
        name=get_name(db_name,'users',user_name)
        st.session_state['user_info']["name"]=name

    app_name = streamlit_js_eval(js_expressions="localStorage.getItem('app_name')",key="Four")
    if app_name and app_name!="nothing":
        main_page=False
        if app_name=="bank_statements":
            try:
                if st.sidebar.button("Go to Main Page"):
                    main_page=True
                if main_page:
                    # cookies["app_name"]="nothing"
                    streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'nothing')",key="three")
                    # cookies.save()
                    app_name="nothing"
                    time.sleep(1)
                    refresh_page()
                    
                db_df=pd.DataFrame()
                dummy_data_file_path = DUMMY_DATA_PATH
                dummy_data = pd.read_excel(dummy_data_file_path)
                  
                st.sidebar.write(f"<p style='margin-bottom: 5px;'>Logged in as {name}</p>", unsafe_allow_html=True)
                st.sidebar.markdown("---")
                    
                # sorting list of banks
                bank_list.sort()

                # Sidebar with bank selection dropdown and file upload
                bank = st.sidebar.selectbox("Select Bank", bank_list)

                # Hide the default "Limit 200MB per file" message using CSS
                st.markdown("""
                    <style>
                        div[data-testid="stFileUploader"] section div {
                            visibility: hidden;
                            height: 0px;
                        }
                        div[data-testid="stFileUploaderDropzoneInstructions"] {
                            display: none !important;
                        }
                        section[data-testid="stFileUploaderDropzone"] {
                            display: flex; /* Ensures proper alignment */
                            justify-content: center;
                            align-items: center;
                            width: fit-content;
                            height: fit-content;
                            background: none; /* Remove any background */
                            padding: 0;
                            margin: 0;
                            border: none;
                        }
                    </style>
                """, unsafe_allow_html=True)

                uploaded_files = st.sidebar.file_uploader(f"Upload Statements (Max size: 2MB)", type=["xls", "xlsx", "pdf"],accept_multiple_files=True)

                file_size_in_limit = True

                # Text input for account holder's name
                ac_name = st.sidebar.text_input("Account Holder's Name:", placeholder="Enter account holder's name here...")
                ac_name=ac_name.strip()

                override=False

                # Initialize session state for confirmation popup
                if "ok" not in st.session_state:
                    st.session_state.ok = False

                def ok_submission():
                    st.session_state.ok = True
                    
                # Sidebar elements to add data
                with st.sidebar:
                    # Submit button inside sidebar
                    st.button("Add data", on_click=ok_submission ,use_container_width=True)
                    block = st.sidebar.empty()
                    st.markdown("""
                    <style>
                        .st-emotion-cache-1gwvy71{
                            padding-bottom:0rem;
                        }
                    </style>
                """, unsafe_allow_html=True)
                    st.sidebar.markdown(
                        """
                        <div style="height: 150px;">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if "Select_data_button" not in st.session_state:
                    st.session_state.Select_data_button = False

                if "delete_all" not in st.session_state:
                    st.session_state.delete_all = False

                # Initialize session state for confirmation popup
                if "confirm" not in st.session_state:
                    st.session_state.confirm = False

                def confirm_submission():
                    st.session_state.confirm = True

                # Sidebar elements to delete data
                with st.sidebar:
                    st.sidebar.markdown("---")
                    # Submit button inside sidebar
                    st.button("Delete my data", on_click=confirm_submission,use_container_width=True)


                if st.sidebar.button("Log out",use_container_width=True):
                    authenticator.logout()


                # get data from db
                db_df=get_transaction_data(db_name,user_name)

                summary_df=get_summary_data(db_name,summ_table)

                # Convert the Date column to datetime and then format it
                summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'],errors='coerce')
                summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'],errors='coerce')

                start_dt=summary_df['Start_Date'].min()
                end_dt=summary_df['End_Date'].max()

                summary_df['Start_Date'] =summary_df['Start_Date'].dt.strftime('%d-%b-%Y')
                summary_df['End_Date'] = summary_df['End_Date'].dt.strftime('%d-%b-%Y')

                # Convert the Date column to datetime
                db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce')

                common_data=pd.DataFrame()
                ex_balance_sum = db_df['Credit'].sum() - db_df['Debit'].sum()
                                
                
                # Show confirmation inside sidebar
                if st.session_state.ok:
                    for uf in uploaded_files:
                        if uf.size > 1024*2048:
                            file_size_in_limit=False
                            break
                    if file_size_in_limit:
                        # If a file is uploaded
                        if uploaded_files:
                            try:
                                n=len(uploaded_files)
                                df=pd.DataFrame()
                                for i in range(n):
                                    tdf=format_uploaded_file(uploaded_files[i],bank,
                                    db_name,user_name)
                                    df=pd.concat([df,tdf])

                                df = df[df['Narration'] != 'OPENINGBALANCE...']
                                # Default name if ac_name is not entered
                                if not ac_name:
                                    ac_name=name
                                df['Name'] = ac_name

                                From=min(pd.to_datetime(df['Date'],errors='coerce'))
                                Till=max(pd.to_datetime(df['Date'],errors='coerce'))

                                # Add a new columna 'Bank' and 'Name'
                                df['Bank'] = bank

                                df = df[['Name','Bank','Date','Narration','Debit','Credit','Category','Balance']]

                                # Ensure Date column is in the same format
                                df['Date'] = pd.to_datetime(df['Date'])

                                # Ensure numeric columns have consistent types
                                df['Debit'] = df['Debit'].astype(float)
                                df['Credit'] = df['Credit'].astype(float)
                                db_df['Debit'] = db_df['Debit'].astype(float)
                                db_df['Credit'] = db_df['Credit'].astype(float)

                                # Strip whitespace and standardize text columns (optional)
                                text_cols = ['Name', 'Bank', 'Narration', 'Category']
                                for col in text_cols:
                                    df[col] = df[col].str.strip()
                                    db_df[col] = db_df[col].str.strip()

                                common_data = has_common_rows(df,db_df)
                                if common_data.empty:
                                    if not df.empty:
                                        ex_balance_sum += df['Credit'].sum() - df['Debit'].sum()
                                        add_data(df,override,db_name,user_name)
                                        if not db_df.empty:
                                            condition_summ = f"Name='{ac_name}' and Bank='{bank}';"
                                            delete_data(db_name,summ_table,condition_summ)
                                        res = get_oldest_latest_date(ac_name,bank,user_name)

                                        if res:
                                            row_condition=f"where Date='{res['oldest_date']}' limit 1"
                                            row = get_transaction_data(db_name,user_name,row_condition)
                                            res['oldest_date']=pd.to_datetime(res['oldest_date'], errors='coerce')
                                            row.loc[0, 'Balance'] += row.loc[0, 'Debit'] - row.loc[0, 'Credit']
                                            openning_bal=row.loc[0, 'Balance']
                                            row.loc[0, 'Balance']+=ex_balance_sum
                                            update_summary1(db_name,summ_table,row.iloc[0]['Name'],bank,res['oldest_date'],res['latest_date'],res['no_of_transactions'],row.loc[0, 'Balance'],openning_bal)
                                        
                                    st.toast(":green[Data updated successfully]")
                                    time.sleep(1.5)
                                    refresh_page()
                                        
                            except Exception as e:
                                st.session_state.ok=False
                                print(f"Error in adding data: {e}")
                                st.toast(":red[The uploaded bank statement does not match the selected bank.]")
                        
                        else:
                            st.session_state.ok=False
                            # Display an error message if there is no data
                            st.toast("Choose a Bank from the dropdown and upload the bank statement to get started.")

                    else:
                        st.session_state.ok=False
                        st.toast(":red[Please upload files smaller than 2MB.]")


                if not common_data.empty:
                    tabs=st.tabs(["Duplicate data"])
                    with tabs[0]:
                        st.warning("These transactions already exists. What would you like to do?")
                        
                        common_data=common_data[['Name','Bank','Date','Narration','Debit','Credit']]
                        common_data['Date']=common_data['Date'].dt.strftime('%d-%b-%Y')
                        display_data(common_data,300,[],True)

                        cll = st.columns(5)
                        with cll[0]:
                            overwrite = st.button("Overwrite",use_container_width=True)
                        with cll[1]:
                            keep = st.button("Keep Both",use_container_width=True)
                        with cll[2]:
                            cancel = st.button("Cancel",use_container_width=True)

                        if overwrite:
                            # Remove exact matches
                            df = df.merge(db_df, on=df.columns.tolist(), how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
                            if not df.empty:
                                ex_balance_sum += df['Credit'].sum() - df['Debit'].sum()
                                add_data(df,override,db_name,user_name)
                                condition_summ = f"Name='{ac_name}' and Bank='{bank}';"
                                delete_data(db_name,summ_table,condition_summ)
                                res = get_oldest_latest_date(ac_name,bank,user_name)

                                if res:
                                    row_condition=f"where Date='{res['oldest_date']}' limit 1"
                                    row = get_transaction_data(db_name,user_name,row_condition)
                                    res['oldest_date']=pd.to_datetime(res['oldest_date'], errors='coerce')
                                    row.loc[0, 'Balance'] += row.loc[0, 'Debit'] - row.loc[0, 'Credit']
                                    openning_bal=row.loc[0, 'Balance']
                                    row.loc[0, 'Balance']+=ex_balance_sum
                                    update_summary1(db_name,summ_table,row.iloc[0]['Name'],bank,res['oldest_date'],res['latest_date'],res['no_of_transactions'],row.loc[0, 'Balance'],openning_bal)

                            st.toast(":green[Data updated successfully]")   
                            time.sleep(1.5)
                            refresh_page()                                

                        elif keep:
                            if not df.empty:
                                ex_balance_sum += df['Credit'].sum() - df['Debit'].sum()
                                add_data(df,override,db_name,user_name)                                    
                                condition_summ = f"Name='{ac_name}' and Bank='{bank}';"
                                delete_data(db_name,summ_table,condition_summ)
                                res = get_oldest_latest_date(ac_name,bank,user_name)

                                if res:
                                    row_condition=f"where Date='{res['oldest_date']}' limit 1"
                                    row = get_transaction_data(db_name,user_name,row_condition)
                                    res['oldest_date']=pd.to_datetime(res['oldest_date'], errors='coerce')                                        
                                    row.loc[0, 'Balance'] += row.loc[0, 'Debit'] - row.loc[0, 'Credit']
                                    openning_bal=row.loc[0, 'Balance']
                                    row.loc[0, 'Balance']+=ex_balance_sum
                                    update_summary1(db_name,summ_table,row.iloc[0]['Name'],bank,res['oldest_date'],res['latest_date'],res['no_of_transactions'],row.loc[0, 'Balance'],openning_bal)
                            st.toast(":green[Data updated successfully]")
                            time.sleep(1.5)
                            refresh_page()

                        elif cancel:
                            refresh_page()

                elif st.session_state.confirm:
                    tab=st.tabs(["Delete"])
                    with tab[0]:
                        if not summary_df.empty:
                            display_data(summary_df,200,[],True)
                        
                        del_cols=st.columns([2,2.7,2,3.3])
                        with del_cols[0]:
                            if st.button("Delete All data"):
                                st.session_state.Select_data_button=False
                                st.session_state.delete_all=True
                                # st.rerun()
                        
                        yp_button1=False
                        can_button1=False
                        yp_button=False
                        can_button=False

                        if st.session_state.delete_all and not st.session_state.Select_data_button:
                            if not db_df.empty:
                                st.warning("This will delete your all data and cannot be undone. Are you sure to proceed?")
                                col1, col2 = st.columns(2)

                                with col1:
                                    if st.button("Yes, Proceed",key="yp2"):
                                        yp_button1=True

                                with col2:
                                    if st.button("Cancel",key="can2"):
                                        can_button1=True

                                if yp_button1:
                                    try:
                                        delete_data(db_name,user_name,"1=1")
                                        delete_data(db_name,summ_table,"1=1")
                                    except Exception as e:
                                        print(f"Error in deleting: {e}")
                                        st.toast(":red[Something went wrong.Please try again.]")
                                    time.sleep(1.5)
                                    refresh_page()
                                
                                if can_button1:
                                    refresh_page()

                            else:
                                st.toast(":red[There are no transactions in your account. No data to delete!]")
                                time.sleep(1.5)
                                refresh_page()

                        with del_cols[1]:
                            if st.button("Delete Selected Data"):
                                st.session_state.delete_all=False
                                st.session_state.Select_data_button=True
                                # st.rerun()

                        if st.session_state.Select_data_button and not st.session_state.delete_all:
                            if not db_df.empty:
                                name_options = list(db_df["Name"].unique())
                                bank_options = list(db_df["Bank"].unique())

                                d = st.columns(4)
                                name_selected,bank_selected="",""

                                # Dropdown to select a name and bank
                                with d[0]:
                                    name_selected = st.selectbox("Select Name:", options=name_options)

                                with d[1]:
                                    bank_selected = st.selectbox("Select Bank:", options=bank_options)

                                with d[2]:
                                    s_date = st.date_input("Pick a start date", value=start_dt,min_value=start_dt,max_value=end_dt)
                                    s_date = s_date.strftime('%Y-%m-%d')

                                with d[3]:
                                    e_date = st.date_input("Pick a end date", value=end_dt,min_value=start_dt,max_value=end_dt)
                                    e_date = e_date.strftime('%Y-%m-%d')
                                
                                condition = f"Date between '{s_date}' and '{e_date}' and Name='{name_selected}' and Bank='{bank_selected}';"
                                condition_summ = f"Name='{name_selected}' and Bank='{bank_selected}';"
                                
                                st.warning(f"This will delete your data Date between '{s_date}' and '{e_date}' for Name '{name_selected}' & Bank '{bank_selected}' and cannot be undone. Are you sure to proceed?")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if st.button("Yes, Proceed", key="yp1"):
                                        yp_button=True
                                with col2:
                                    if st.button("Cancel",key="can1"):
                                        can_button=True
                                
                                if yp_button:
                                    try:
                                        delete_data(db_name,user_name,condition)
                                        delete_data(db_name,summ_table,condition_summ)
                                        res = get_oldest_latest_date(name_selected,bank_selected,user_name)

                                        if res:
                                            row_condition=f"where Date='{res['oldest_date']}' limit 1"
                                            row = get_transaction_data(db_name,user_name,row_condition)
                                            res['oldest_date']=pd.to_datetime(res['oldest_date'], errors='coerce')
                                            row.loc[0, 'Balance'] += row.loc[0, 'Debit'] - row.loc[0, 'Credit']
                                            openning_bal=row.loc[0, 'Balance']
                                            cred_deb_condition=f"where Bank='{bank_selected}' and Name='{name_selected}'"
                                            cred_deb_df=get_transaction_data(db_name,user_name,cred_deb_condition)
                                            cred_deb_sum = cred_deb_df['Credit'].sum() - cred_deb_df['Debit'].sum() + row.loc[0, 'Balance']
                                                
                                            update_summary1(db_name,summ_table,row.iloc[0]['Name'],bank,res['oldest_date'],res['latest_date'],res['no_of_transactions'],cred_deb_sum,openning_bal)
                                        st.toast(":green[Data deleted successfully]")
                                    except Exception as e:
                                        print(f"Error in deleting: {e}")
                                        st.toast(":red[Something went wrong.Please try again.]")
                                    st.session_state.confirm = False
                                    time.sleep(1.5)
                                    refresh_page()
                                        
                                if can_button:
                                    refresh_page()
                            else:
                                st.toast(":red[There are no transactions in your account. No data to delete!]")
                                time.sleep(1.5)
                                refresh_page()

                        with del_cols[2]:
                            if st.button("Go Back"):
                                refresh_page()
                else:
                    if user_name in admins:
                        # Apply CSS to reduce white space above tabs
                        st.markdown(
                            """
                            <style>
                                div.block-container { padding-top: 0rem; } /* Reduce padding */
                                div[data-testid="stTabs"] { margin-top: -50px; } /* Move tabs higher */
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
                        # Create tabs
                        tab1, tab2, tab3, tab4, tab5, tab6= st.tabs(["Dashboard", "Summary", "Bank Entries", "Feedback","Razorpay","Categories"])
                    else:
                        # Apply CSS to reduce white space above tabs
                        st.markdown(
                            """
                            <style>
                                div.block-container { padding-top: 0rem; } /* Reduce padding */
                                div[data-testid="stTabs"] { margin-top: -50px; } /* Move tabs higher */
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
                        # Create tabs
                        tab1, tab2, tab3, tab4= st.tabs(["Dashboard", "Summary", "Bank Entries", "Feedback"])

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
                                g_df_hichart=db_df[['Name','Bank','Date','Narration','Debit','Credit','Category']].copy()
                                g_df_hichart["Date"] = pd.to_datetime(g_df_hichart["Date"])  # Convert Date column to datetime
                                g_df_hichart["Year"] = g_df_hichart["Date"].dt.year
                                g_df_hichart["Month"] = g_df_hichart["Date"].dt.strftime("%B")
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
                                    display_hicharts(g_df_hichart,selected_name,selected_bank)
                                    display_hichart2(g_df_hichart,selected_name,selected_bank)
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
                                g_df_hichart=dummy_data.copy()
                                g_df_hichart["Date"] = pd.to_datetime(g_df_hichart["Date"])  # Convert Date column to datetime
                                g_df_hichart["Year"] = g_df_hichart["Date"].dt.year
                                g_df_hichart["Month"] = g_df_hichart["Date"].dt.strftime("%B")
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
                                    display_hicharts(g_df_hichart,selected_name,selected_bank)
                                    display_hichart2(g_df_hichart,selected_name,selected_bank)
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
                                table_nm="Categories"
                                initialize_db(table_nm)
                                category_table_data = get_categories(table_nm)
                                with st.container():
                                    download_df = db_df.copy()
                                    download_df['Date'] = pd.to_datetime(download_df['Date'],errors='coerce')
                                    display_transaction_data(db_df,600,download_df,False,db_name,user_name,sorted(category_table_data['Category'].unique()))
                                    # db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce')
                                    # st.download_button(
                                    #     key='dbs',
                                    #     label="Download data",
                                    #     data=convert_df_to_excel(db_df),
                                    #     file_name="bank_statement.xlsx",
                                    #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    # )
                            else:
                                if st.button("Show Dummy Data",key='showd2'):
                                    dummy_data['Date'] = dummy_data['Date'].dt.strftime('%d-%b-%Y')
                                    display_data(dummy_data,600,[],True)
                                    dummy_data['Date'] = pd.to_datetime(dummy_data['Date'],errors='coerce')
                                

                        except Exception as e:
                            print(f"Error in fetching transction data: {e}")
                            st.toast(":red[Something went wrong.]")
                    
                    with tab2:
                        try:
                            if not db_df.empty:
                                # st.subheader("Summary")
                                if not summary_df.empty:# Rename columns
                                    old_col_names=["Start_Date","End_Date","Pending_days","Opening_balance","Closing_balance"]
                                    new_col_names=["Start Date","End Date","Pending days","Opening balance","Closing balance"]
                                    rename_dict = {o: n for o, n in zip(old_col_names, new_col_names) if o in summary_df.columns}
                                    summary_df=summary_df.rename(columns=rename_dict)

                                    display_data(summary_df,200,[],True)

                                    rename_dict = {o: n for o, n in zip(new_col_names,old_col_names) if o in summary_df.columns}
                                    summary_df=summary_df.rename(columns=rename_dict)

                                    # Convert the Date column to datetime and then format it
                                    summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'],errors='coerce')
                                    summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'],errors='coerce')
                                    with st.container():
                                        col1, col2= st.columns([4, 1])  # Added extra spacing
                                        with col2:
                                            st.download_button(
                                                key='dbs_summary',
                                                label="Download data",
                                                data=convert_df_to_excel(summary_df),
                                                file_name="bank_statement_summary.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                            )
                            else:
                                if st.button("Show Dummy Summary",key='showd1'):
                                    dummy_summary_data_file_path = DUMMY_DATA_SUMMARY_PATH
                                    dummy_summary_data=pd.read_excel(dummy_summary_data_file_path)
                                    # Convert the Date column to datetime and then format it
                                    dummy_summary_data['Start_Date'] = pd.to_datetime(dummy_summary_data['Start_Date'],errors='coerce').dt.strftime('%d-%b-%Y')
                                    dummy_summary_data['End_Date'] = pd.to_datetime(dummy_summary_data['End_Date'],errors='coerce').dt.strftime('%d-%b-%Y')

                                    display_data(dummy_summary_data,300,[],True)

                        except Exception as e:
                            print(f"Error in fetching summary data: {e}")
                            st.toast(":red[Something went wrong.]")
                    
                    with tab4:
                        # Admin Email Config
                        ADMIN_EMAILS=[ADMIN_EMAIL1,ADMIN_EMAIL2]

                        SMTP_SERVER = SMTP_SERVER

                        SMTP_USER = SMTP_USER  # Replace with your Gmail
                        SMTP_PASSWORD = email_pass  # Use an App Password, not your main password
                        feedback_table='Feedback'
                        st.write("**We value your thoughts! Feel free to share any feedback, ideas, or suggestions to help us improve. Your insights make a difference!**")

                        # Text area for feedback
                        feedback = st.text_area("Your Feedback:", placeholder="Write your feedback here...",height=150)
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

                    if user_name in admins:
                        with tab5:
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
                                                "name": "Alpha Aces Advisory LLP",
                                                "description": "Payment for Order",
                                                "order_id": "{order['id']}",
                                                "handler": function (response) {{
                                                    // You can handle the response here after successful payment
                                                    //console.log(response);
                                                    //window.location.href = "/?payment=success";
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

                        with tab6:
                            table_nm="Categories"
                            initialize_db(table_nm)
                            # Initialize session state for table data
                            if "table_data" not in st.session_state:
                                st.session_state.table_data = get_categories(table_nm)

                            # Session state to track replace prompt
                            if "replace_prompt" not in st.session_state:
                                st.session_state.replace_prompt = False
                                st.session_state.pending_category = None
                                st.session_state.pending_keyword = None
                                st.session_state.existing_category = None

                            # Function to refresh the table
                            def refresh_table():
                                time.sleep(3)
                                st.rerun()

                            # Add New Entry Section
                            st.subheader("Add New Item")

                            col = st.columns(3)  # Layout columns

                            # Unique categories sorted A-Z
                            unique_categories = sorted(st.session_state.table_data["Category"].unique())
                            new_category = col[0].selectbox("Select Category", ["Add new category"]+unique_categories, index=0)

                            if new_category == "Add new category":
                                new_category = col[1].text_input("Enter New Category")

                            next_col=st.columns(3)
                            new_keywords = next_col[0].text_input("Enter comma-separated Keywords")
                            type = next_col[1].selectbox("Select Transaction type",["Credit","Debit"])
                            
                            message_to_display=""
                            success_message=False

                            with next_col[2]:
                                # Move button slightly up
                                st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)  # Adds margin
                                # Check for duplicate and show prompt
                                if st.button("Add", use_container_width=True):
                                    keyword_list = [item for item in new_keywords.split(",") if item]
                                    if new_category and new_keywords:
                                        for new_keyword in keyword_list:
                                            existing_entry = st.session_state.table_data[(st.session_state.table_data["Keyword"] == new_keyword) & (type==st.session_state.table_data["Type"])]

                                            if not existing_entry.empty:
                                                # Store the existing keyword/category in session state
                                                st.session_state.pending_category = new_category
                                                st.session_state.pending_keyword = new_keyword
                                                st.session_state.existing_category = existing_entry.iloc[0]["Category"]
                                                # st.session_state.replace_prompt = True

                                            else:
                                                success_message=True
                                                # Add new entry since no duplicate exists
                                                for new_keyword in keyword_list:
                                                    new_entry = pd.DataFrame({"Keyword": [new_keyword], "Category": [new_category], "Type":[type]})
                                                    st.session_state.table_data = pd.concat([st.session_state.table_data, new_entry], ignore_index=True)
                                                delete_all(table_nm)
                                                add_category_df(st.session_state.table_data,table_nm)
                                                message_to_display=f"✅ Added: {new_category} - {keyword_list}"

                                                
                                    else:
                                        success_message=False
                                        message_to_display="⚠ Please enter both Category and Keyword!"

                            if message_to_display!="":
                                if not success_message:
                                    st.error(message_to_display)
                                else:
                                    st.success(message_to_display)
                                message_to_display=""
                                refresh_table()

                            # Display the table
                            st.subheader("Category & Keyword Table")

                            gb = GridOptionsBuilder.from_dataframe(st.session_state.table_data)

                            # Add checkbox selection
                            gb.configure_selection(selection_mode="multiple", use_checkbox=True)

                            # Build grid options
                            grid_options = gb.build()

                            # Render AgGrid
                            grid_response = AgGrid(
                                st.session_state.table_data,
                                gridOptions=grid_options,
                                height=300,
                                fit_columns_on_grid_load=True
                            )

                            # Get selected rows as a DataFrame
                            selected_rows = pd.DataFrame(grid_response["selected_rows"])

                            # Delete Selected Rows
                            if not selected_rows.empty and st.button("❌ Delete Selected Rows"):
                                st.session_state.table_data = st.session_state.table_data.merge(selected_rows, how="left", indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
                                delete_all(table_nm)
                                add_category_df(st.session_state.table_data,table_nm)
                                refresh_table()

                            # Handle Replace Prompt
                            if st.session_state.replace_prompt:
                                st.warning(f"⚠ The keyword **'{st.session_state.pending_keyword}'** already exists under **'{st.session_state.existing_category}'** category.")
                                
                                colA, colB = st.columns(2)
                                
                                if colA.button("🔄 Replace Existing"):
                                    st.session_state.table_data.loc[st.session_state.table_data["Keyword"] == st.session_state.pending_keyword, "Category"] = st.session_state.pending_category
                                    st.session_state.replace_prompt = False
                                    refresh_table()
                                
                                if colB.button("❌ Cancel"):
                                    st.session_state.replace_prompt = False
                                    refresh_table()
            except Exception as e:
                print(f"Error in fetching data : {e}")
                st.toast(":red[Something went wrong.Please try again.]")
                # delete_data(db_name,user_name,"Name is NULL")
                time.sleep(2)
                authenticator.logout()
                # refresh_page()
        elif app_name=="networth":
            if st.sidebar.button("Go to Main Page"):
                main_page=True
            if main_page:
                streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'nothing')",key="two")
                # cookies.save()
                app_name="nothing"
                time.sleep(1)
                refresh_page()
            st.sidebar.write(f"<p style='margin-bottom: 5px;'>Logged in as {name}</p>", unsafe_allow_html=True)
            st.sidebar.markdown("---")
            networth(authenticator)
        else:
            st.write("### 📊 Welcome to the Null!")

    else:
        # Sidebar dropdown to select an app
        app_name = st.sidebar.selectbox("📂 Select an App", list(apps.keys()))
        app_name=apps[app_name]
        if st.sidebar.button("Open app",use_container_width=True):
            streamlit_js_eval(js_expressions=f"localStorage.setItem('app_name', '{app_name}')",key="One")
            time.sleep(1)
            refresh_page()
        
        st.markdown("""
        <style>
            .st-emotion-cache-1gwvy71{
                padding-bottom:0rem;
            }
        </style>
    """, unsafe_allow_html=True)
        
        st.sidebar.markdown(
            """
            <div style="height: 500px;">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")
        if st.sidebar.button("Log out",use_container_width=True):
            authenticator.logout()
  
else:
    auth_url=authenticator.login()
    if not auth_url:
        st.error("Authentication URL is not available.")
    else:
        css = """
                <style>
                    header[data-testid="stHeader"]{
                        z-index:1000;
                  }
                    .gcenter {
                        margin-top:1.5rem;
                        hieght:100px;
                        overflow-x:hidden;
                        width: 100vw;
                        display: flex;
                        position:fixed;
                        top: 1vh;
                        left:6vw;
                        background-color:white;
                        z-index: 1000000000000000;
                    }
                    .google-button {
                        background-color: #4285F4;
                        color: white !important;
                        border-radius: 5px;
                        padding: 10px 15px;
                        font-size: 1.5rem;
                        border: none;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        text-decoration: none !important;
                        gap: 5px;
                    }
                    .google-button img {
                        width: 1.5rem;
                        height: 1.5rem;
                        margin-left: 5px;
                        border-radius: 50%;
                    }
                    /* Media query for screens 768px and smaller */
                    @media (max-width: 1100px) {
                        .gcenter {
                            background-color:white
                            position: fixed;
                            top: 1vh;
                            left: 50%;
                            transform: translateX(-50%); /* Moves it to center */
                            width: max-content; /* Adjust width based on content */
                            display: flex;
                            justify-content: center; /* Ensures content is centered */
                            align-items: center; /* Vertically aligns the button */
                        }
                        .google-button {
                            padding: 8px 12px;
                            font-size: 1.2rem;
                        }
                    }
                                        /* Media query for mobile-sized screens */
                    @media (max-width: 480px) {
                        .google-button {
                            padding: 6px 10px;
                            font-size: 1rem;
                        }
                    }
                </style>
            """

        html = f"""
            <div class="gcenter">
                <a href="{auth_url}" class="google-button" target="_self">
                    Login with Google
                    <img src="https://icon2.cleanpng.com/lnd/20241121/sc/bd7ce03eb1225083f951fc01171835.webp"  alt="Google logo" />
                </a>
            </div>
        """

        st.markdown(css, unsafe_allow_html=True)
        st.markdown(html, unsafe_allow_html=True)
    show_message(page)
