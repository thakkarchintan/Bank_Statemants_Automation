import streamlit as st
import os
st.set_page_config(page_title="Fintellect", page_icon=os.getenv("Fevicon_Path"), layout="wide",initial_sidebar_state="expanded")
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
        /* Remove extra space above tabs */
        .stTabs [data-baseweb="tab-list"] {
            margin-top: -50px;
        }
        /* Adjust button height */
        .stButton button {
            height: 38px;
        }
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
page = query_params.get("page", ["home"])[0]

authenticator = Authenticator(
    token_key=TOKEN_KEY,
    secret_path=SECRET_PATH,
    redirect_uri=REDIRECT_URI,
)

authenticator.check_auth()

db_name = DATABASE
# Define available finance-related apps
apps = {
    "🏦 Bank Statements Analyzer": "bank_statements",
    "📊 Net Worth Tracker": "networth",
}

if st.session_state["connected"]:
    user_info = st.session_state['user_info']
    name = user_info.get('name')
    g_id = user_info.get('id')
    if g_id:
        user_email = str(user_info.get('email'))
        streamlit_js_eval(js_expressions=f"localStorage.setItem('local_email', '{user_email}')", key="el")
        time.sleep(2)
    else:
        user_email = str(streamlit_js_eval(js_expressions="localStorage.getItem('local_email')", key="ef"))
        time.sleep(2)
        st.session_state['user_info']["email"] = user_email
    user_name = user_email[:-10]
    user_name = user_name.replace('.', '__')
    summ_table = user_name + '_summary'
    user_status = check_user_status(user_email)

    if g_id:
        user_data = (user_name, user_info.get('name'), user_email)
        add_user(db_name, 'users', user_data)
    else:
        name = get_name(db_name, 'users', user_name)
        st.session_state['user_info']["name"] = name

    if user_name in admins or (user_status and user_status['is_approved']) :
        app_name = streamlit_js_eval(js_expressions="localStorage.getItem('app_name')", key="Four")
        if app_name and app_name != "nothing":
            main_page = False
            if app_name == "bank_statements":
                try:
                    if st.sidebar.button("Go to Main Page"):
                        main_page = True
                    if main_page:
                        streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'nothing')", key="three")
                        app_name = "nothing"
                        time.sleep(1)
                        refresh_page()

                    db_df = pd.DataFrame()
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

                    uploaded_files = st.sidebar.file_uploader(f"Upload Statements (Max size: 2MB)", type=["xls", "xlsx", "pdf"], accept_multiple_files=True)

                    file_size_in_limit = True

                    # Text input for account holder's name
                    ac_name = st.sidebar.text_input("Account Holder's Name:", placeholder="Enter account holder's name here...")
                    ac_name = ac_name.strip()

                    override = False

                    # Initialize session state for confirmation popup
                    if "ok" not in st.session_state:
                        st.session_state.ok = False

                    def ok_submission():
                        st.session_state.ok = True

                    # Sidebar elements to add data
                    with st.sidebar:
                        # Submit button inside sidebar
                        st.button("Add data", on_click=ok_submission, use_container_width=True)
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
                        st.button("Delete my data", on_click=confirm_submission, use_container_width=True)

                    if st.sidebar.button("Log out", use_container_width=True):
                        authenticator.logout()

                    # st.experimental_set_query_params(placeholder="") 
                    # with st.spinner("Refreshing Data ..."):
                    # get data from db
                    db_df = get_transaction_data(db_name, user_name,"order by Name,Bank,Date")

                    summary_df = get_summary_data(db_name, summ_table)

                    # Convert the Date column to datetime and then format it
                    summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'], errors='coerce')
                    summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'], errors='coerce')

                    start_dt = summary_df['Start_Date'].min()
                    end_dt = summary_df['End_Date'].max()

                    summary_df['Start_Date'] = summary_df['Start_Date'].dt.strftime('%d-%b-%Y')
                    summary_df['End_Date'] = summary_df['End_Date'].dt.strftime('%d-%b-%Y')

                    # Convert the Date column to datetime
                    db_df['Date'] = pd.to_datetime(db_df['Date'], errors='coerce')

                    common_data = pd.DataFrame()
                    ex_balance_sum = 0

                    # Show confirmation inside sidebar
                    if st.session_state.ok:
                        for uf in uploaded_files:
                            if uf.size > 1024 * 2048:
                                file_size_in_limit = False
                                break
                        if file_size_in_limit:
                            # If a file is uploaded
                            if uploaded_files:
                                try:
                                    n = len(uploaded_files)
                                    df = pd.DataFrame()
                                    for i in range(n):
                                        tdf = format_uploaded_file(uploaded_files[i], bank,
                                                                db_name, user_name)
                                        df = pd.concat([df, tdf])

                                    df = df[df['Narration'] != 'OPENINGBALANCE...']
                                    # Default name if ac_name is not entered
                                    if not ac_name:
                                        ac_name = name
                                    df['Name'] = ac_name

                                    From = min(pd.to_datetime(df['Date'], errors='coerce'))
                                    Till = max(pd.to_datetime(df['Date'], errors='coerce'))

                                    # Add a new columna 'Bank' and 'Name'
                                    df['Bank'] = bank

                                    df = df[['Name', 'Bank', 'Date', 'Narration', 'Debit', 'Credit', 'Category', 'Balance']]

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

                                    bank_name_filtered_df = db_df[(db_df['Name'] == ac_name) & (db_df['Bank'] == bank)]
                                    sum_debit = bank_name_filtered_df['Debit'].sum()
                                    sum_credit = bank_name_filtered_df['Credit'].sum()
                                    ex_balance_sum=sum_credit-sum_debit
                                    
                                    if not df.empty:
                                        ex_balance_sum += df['Credit'].sum() - df['Debit'].sum()
                                        add_data(df, override, db_name, user_name)
                                        if not db_df.empty:
                                            condition_summ = f"Name='{ac_name}' and Bank='{bank}';"
                                            delete_data(db_name, summ_table, condition_summ)
                                        res = get_oldest_latest_date(ac_name, bank, user_name)

                                        if res:
                                            row_condition = f"where Date='{res['oldest_date']}' and Name='{ac_name}' and Bank='{bank}' limit 1"
                                            row = get_transaction_data2(db_name, user_name, row_condition)
                                            res['oldest_date'] = pd.to_datetime(res['oldest_date'], errors='coerce')
                                            row.loc[0, 'Balance']=float(row.loc[0, 'Balance'])
                                            row.loc[0, 'Balance'] += float(row.loc[0, 'Debit']) - float(row.loc[0, 'Credit'])
                                            openning_bal = row.loc[0, 'Balance']
                                            # print(row.loc[0, 'Balance'])
                                            row.loc[0, 'Balance'] += ex_balance_sum
                                            update_summary1(db_name, summ_table, row.iloc[0]['Name'], bank,
                                                        res['oldest_date'], res['latest_date'],
                                                        res['no_of_transactions'], row.loc[0, 'Balance'],
                                                        openning_bal)

                                    st.toast(":green[Data updated successfully]")
                                    st.cache_data.clear()
                                    time.sleep(1.5)
                                    refresh_page()

                                except Exception as e:
                                    st.session_state.ok = False
                                    print(f"Error in adding data: {e}")
                                    st.toast(":red[The uploaded bank statement does not match the selected bank.]")

                            else:
                                st.session_state.ok = False
                                # Display an error message if there is no data
                                st.toast("Choose a Bank from the dropdown and upload the bank statement to get started.")

                        else:
                            st.session_state.ok = False
                            st.toast(":red[Please upload files smaller than 2MB.]")

               
                    elif st.session_state.confirm:
                        # Apply CSS to reduce space above tabs in the "Delete Data" section
                        st.markdown(
                            """
                            <style>
                                div.block-container { padding-top: 0rem; } /* Reduce padding */
                                div[data-testid="stTabs"] { margin-top: -110px; } /* Move tabs higher */
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
                        tab = st.tabs(["Delete"])
                        with tab[0]:
                            if not summary_df.empty:
                                display_data(summary_df, 200, [], True)

                            del_cols = st.columns([2, 2.7, 2, 3.3])
                            with del_cols[0]:
                                if st.button("Delete All data", use_container_width=True):
                                    st.session_state.Select_data_button = False
                                    st.session_state.delete_all = True
                                    # st.rerun()

                            yp_button1 = False
                            can_button1 = False
                            yp_button = False
                            can_button = False

                            if st.session_state.delete_all and not st.session_state.Select_data_button:
                                if not db_df.empty:
                                    st.warning("This will delete your all data and cannot be undone. Are you sure to proceed?")
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        if st.button("Yes, Proceed", key="yp2"):
                                            yp_button1 = True

                                    with col2:
                                        if st.button("Cancel", key="can2"):
                                            can_button1 = True

                                    if yp_button1:
                                        try:
                                            delete_data(db_name, user_name, "1=1")
                                            delete_data(db_name, summ_table, "1=1")
                                        except Exception as e:
                                            print(f"Error in deleting: {e}")
                                            st.toast(":red[Something went wrong.Please try again.]")
                                        st.cache_data.clear()
                                        time.sleep(1.5)
                                        refresh_page()

                                    if can_button1:
                                        refresh_page()

                                else:
                                    st.toast(":red[There are no transactions in your account. No data to delete!]")
                                    time.sleep(1.5)
                                    refresh_page()

                            with del_cols[1]:
                                if st.button("Delete Selected Data", use_container_width=True):
                                    st.session_state.delete_all = False
                                    st.session_state.Select_data_button = True

                            if st.session_state.Select_data_button and not st.session_state.delete_all:
                                if not db_df.empty:
                                    name_options = list(db_df["Name"].unique())
                                    bank_options = list(db_df["Bank"].unique())

                                    d = st.columns(4)
                                    name_selected, bank_selected = "", ""

                                    # Dropdown to select a name and bank
                                    with d[0]:
                                        name_selected = st.selectbox("Select Name:", options=name_options)

                                    with d[1]:
                                        bank_selected = st.selectbox("Select Bank:", options=bank_options)

                                    with d[2]:
                                        s_date = st.date_input("Pick a start date", value=start_dt, min_value=start_dt,
                                                            max_value=end_dt)
                                        s_date = s_date.strftime('%Y-%m-%d')

                                    with d[3]:
                                        e_date = st.date_input("Pick a end date", value=end_dt, min_value=start_dt,
                                                            max_value=end_dt)
                                        e_date = e_date.strftime('%Y-%m-%d')

                                    condition = f"Date between '{s_date}' and '{e_date}' and Name='{name_selected}' and Bank='{bank_selected}';"
                                    condition_summ = f"Name='{name_selected}' and Bank='{bank_selected}';"

                                    st.warning(
                                        f"This will delete your data Date between '{s_date}' and '{e_date}' for Name '{name_selected}' & Bank '{bank_selected}' and cannot be undone. Are you sure to proceed?")
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        if st.button("Yes, Proceed", key="yp1"):
                                            yp_button = True
                                    with col2:
                                        if st.button("Cancel", key="can1"):
                                            can_button = True

                                    if yp_button:
                                        try:
                                            delete_data(db_name, user_name, condition)
                                            delete_data(db_name, summ_table, condition_summ)
                                            res = get_oldest_latest_date(name_selected, bank_selected, user_name)
                                            # print(res)
                                            if res:
                                                row_condition = f"where Date='{res['oldest_date']}' and Bank='{bank_selected}' and Name='{name_selected}' limit 1"
                                                row = get_transaction_data2(db_name, user_name, row_condition)
                                                # print(row)
                                                res['oldest_date'] = pd.to_datetime(res['oldest_date'], errors='coerce')
                                                row.loc[0, 'Balance'] += row.loc[0, 'Debit'] - row.loc[0, 'Credit']
                                                openning_bal = row.loc[0, 'Balance']
                                                cred_deb_condition = f"where Bank='{bank_selected}' and Name='{name_selected}'"
                                                cred_deb_df = get_transaction_data2(db_name, user_name, cred_deb_condition)
                                                cred_deb_sum = cred_deb_df['Credit'].sum() - cred_deb_df['Debit'].sum() + row.loc[
                                                    0, 'Balance']

                                                update_summary1(db_name, summ_table, row.iloc[0]['Name'], bank_selected,
                                                            res['oldest_date'], res['latest_date'],
                                                            res['no_of_transactions'], cred_deb_sum, openning_bal)
                                                st.toast(":green[Data deleted successfully]")
                                                st.session_state.confirm = False
                                                st.cache_data.clear()
                                                time.sleep(2)
                                                refresh_page()
                                            else:
                                                st.toast(":green[Data deleted successfully]")
                                                st.session_state.confirm = False
                                                st.cache_data.clear()
                                                time.sleep(2)
                                                refresh_page()
                                        except Exception as e:
                                            print(f"Error in deleting: {e}")
                                            st.toast(":red[Something went wrong.Please try again.]")

                                    if can_button:
                                        refresh_page()
                                else:
                                    st.toast(":red[There are no transactions in your account. No data to delete!]")
                                    time.sleep(1.5)
                                    refresh_page()

                            with del_cols[2]:
                                if st.button("Go Back", use_container_width=True):
                                    refresh_page()
                    else:
                        if user_name in admins:
                            # Apply CSS to reduce white space above tabs
                            st.markdown(
                                """
                                <style>
                                    div.block-container { padding-top: 0rem; } /* Reduce padding */
                                    div[data-testid="stTabs"] { margin-top: -110px; } /* Move tabs higher */
                                </style>
                                """,
                                unsafe_allow_html=True
                            )
                            # Create tabs
                            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
                                ["Dashboard", "Summary", "Bank Entries", "Feedback", "Razorpay", "Categories","Beta Version Requests"])
                        else:
                            # Apply CSS to reduce white space above tabs
                            st.markdown(
                                """
                                <style>
                                    div.block-container { padding-top: 0rem; } /* Reduce padding */
                                    div[data-testid="stTabs"] { margin-top: -110px; } /* Move tabs higher */
                                </style>
                                """,
                                unsafe_allow_html=True
                            )
                            # Create tabs
                            tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Summary", "Bank Entries", "Feedback"])

                        # Content for each tab
                        with tab1:
                            try:
                                g_df=db_df.copy()
                                if db_df.empty:
                                    g_df=dummy_data.copy()

                                name_options = ["All"] + list(g_df["Name"].unique())
                                bank_options = ["All"] + list(g_df["Bank"].unique())

                                g_df = g_df[['Name', 'Bank', 'Date', 'Narration', 'Debit', 'Credit', 'Category']]
                                
                                g_df["Date"] = pd.to_datetime(g_df["Date"])
                                g_df['Year'] = g_df['Date'].dt.year.astype(int)  # Convert to integer type
                                g_df['Month'] = g_df['Date'].dt.strftime('%m-%Y')
                                g_df['Category'] = g_df['Category'].fillna('Untagged').astype(str)
                                g_df['Category'] = g_df['Category'].replace("", "Untagged").astype(str)
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
                                    if selected_bank!='All':
                                        g_df = g_df[g_df["Bank"] == selected_bank]
                                    if selected_name!='All':
                                        g_df = g_df[g_df["Name"] == selected_name]

                                    credit_g_df=g_df[g_df['Credit'] != 0]
                                    debit_g_df=g_df[g_df['Debit'] != 0]

                                    cols1=st.columns(2)
                                    with cols1[0]:
                                        top_left(credit_g_df)
                                    with cols1[1]:
                                        top_right(debit_g_df)

                                    cols2=st.columns(2)
                                    with cols2[0]:
                                        bottom_left(credit_g_df)
                                    with cols2[1]:
                                        bottom_right(debit_g_df)

                            except Exception as e:
                                print(f"Error in showing transction data graph: {e}")
                                st.toast(":red[Something went wrong.]")

                        with tab3:
                            try:
                                if not db_df.empty:
                                    db_df['Date'] = db_df['Date'].dt.strftime('%d-%b-%Y')
                                    table_nm = "Categories"
                                    initialize_db(table_nm)
                                    category_table_data = get_categories(table_nm)
                                    with st.container():
                                        download_df = db_df.copy()
                                        download_df['Date'] = pd.to_datetime(download_df['Date'], errors='coerce')
                                        display_data(db_df, 600, download_df, False, db_name, user_name, True,
                                                    sorted(category_table_data['Category'].unique()))
                                        # db_df['Date'] = pd.to_datetime(db_df['Date'],errors='coerce')
                                        # st.download_button(
                                        #     key='dbs',
                                        #     label="Download data",
                                        #     data=convert_df_to_excel(db_df),
                                        #     file_name="bank_statement.xlsx",
                                        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                        # )
                                else:
                                    if st.button("Show Dummy Data", key='showd2'):
                                        dummy_data['Date'] = dummy_data['Date'].dt.strftime('%d-%b-%Y')
                                        display_data(dummy_data, 700, [], True)
                                        dummy_data['Date'] = pd.to_datetime(dummy_data['Date'], errors='coerce')

                            except Exception as e:
                                print(f"Error in fetching transction data: {e}")
                                st.toast(":red[Something went wrong.]")

                        with tab2:
                            try:
                                if not db_df.empty:
                                    # st.subheader("Summary")
                                    if not summary_df.empty:  # Rename columns
                                        old_col_names = ["Start_Date", "End_Date", "Pending_days", "Opening_balance",
                                                        "Closing_balance"]
                                        new_col_names = ["Start Date", "End Date", "Pending days", "Opening balance",
                                                        "Closing balance"]
                                        rename_dict = {o: n for o, n in zip(old_col_names, new_col_names) if
                                                    o in summary_df.columns}
                                        summary_df = summary_df.rename(columns=rename_dict)

                                        display_data(summary_df, 200, [], True)

                                        rename_dict = {o: n for o, n in zip(new_col_names, old_col_names) if
                                                    o in summary_df.columns}
                                        summary_df = summary_df.rename(columns=rename_dict)

                                        # Convert the Date column to datetime and then format it
                                        summary_df['Start_Date'] = pd.to_datetime(summary_df['Start_Date'], errors='coerce')
                                        summary_df['End_Date'] = pd.to_datetime(summary_df['End_Date'], errors='coerce')
                                        with st.container():
                                            col1, col2 = st.columns([1, 4])  # Added extra spacing
                                            with col1:
                                                st.download_button(
                                                    key='dbs_summary',
                                                    label="Download data",
                                                    data=convert_df_to_excel(summary_df),
                                                    file_name="bank_statement_summary.xlsx",
                                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                    use_container_width=True
                                                )
                                else:
                                    if st.button("Show Dummy Summary", key='showd1'):
                                        dummy_summary_data_file_path = DUMMY_DATA_SUMMARY_PATH
                                        dummy_summary_data = pd.read_excel(dummy_summary_data_file_path)
                                        # Convert the Date column to datetime and then format it
                                        dummy_summary_data['Start_Date'] = pd.to_datetime(dummy_summary_data['Start_Date'],
                                                                                        errors='coerce').dt.strftime(
                                            '%d-%b-%Y')
                                        dummy_summary_data['End_Date'] = pd.to_datetime(dummy_summary_data['End_Date'],
                                                                                    errors='coerce').dt.strftime(
                                            '%d-%b-%Y')

                                        display_data(dummy_summary_data, 300, [], True)

                            except Exception as e:
                                print(f"Error in fetching summary data: {e}")
                                st.toast(":red[Something went wrong.]")

                        with tab4:
                            feedback_table = 'Feedback'
                            st.write(
                                "**We value your thoughts! Feel free to share any feedback, ideas, or suggestions to help us improve. Your insights make a difference!**")

                            # Text area for feedback
                            feedback = st.text_area("Your Feedback:", placeholder="Write your feedback here...", height=150)
                            feedback = feedback.strip()

                            # File uploader (Optional)
                            uploaded_file = st.file_uploader("Attach a file (optional)", type=["xls", "xlsx", "pdf", "png", "jpg"])

                            # Submit button
                            if st.button("Submit Feedback"):
                                if feedback:  # Checking if input is not empty
                                    try:
                                        # data = (user_name, feedback)
                                        # add_feedback(db_name, feedback_table, data)
                                        send_email(feedback, user_email, uploaded_file)
                                        st.toast(":green[Thank you for your feedback! It has been sent to the admin.]")
                                        time.sleep(2)
                                        refresh_page()
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
                                try:
                                    table_nm = "Categories"
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
                                    col1, col2, col3, col4, col5 = st.columns(5)  # Layout columns with 5 columns for all elements

                                    # Unique categories sorted A-Z
                                    unique_categories = sorted(st.session_state.table_data["Category"].unique())
                                    new_category = col1.selectbox("Select Category", ["Add new category"] + unique_categories,
                                                                index=0)

                                    if new_category == "Add new category":
                                        new_category = col2.text_input("Enter New Category")

                                    new_keywords = col3.text_input("Enter Keywords")
                                    type = col4.selectbox("Select Transaction type", ["Credit", "Debit"])

                                    message_to_display = ""
                                    success_message = False

                                    with col5:
                                        # Move button slightly up
                                        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)  # Adds margin
                                        # Check for duplicate and show prompt
                                        if st.button("Add", use_container_width=True):
                                            keyword_list = [item for item in new_keywords.split(",") if item]
                                            if new_category and new_keywords:
                                                for new_keyword in keyword_list:
                                                    existing_entry = st.session_state.table_data[
                                                        (st.session_state.table_data["Keyword"] == new_keyword) & (
                                                                type == st.session_state.table_data["Type"])]

                                                    if not existing_entry.empty:
                                                        # Store the existing keyword/category in session state
                                                        st.session_state.pending_category = new_category
                                                        st.session_state.pending_keyword = new_keyword
                                                        st.session_state.existing_category = existing_entry.iloc[0]["Category"]
                                                        # st.session_state.replace_prompt = True

                                                    else:
                                                        success_message = True
                                                        # Add new entry since no duplicate exists
                                                        for new_keyword in keyword_list:
                                                            new_entry = pd.DataFrame(
                                                                {"Keyword": [new_keyword], "Category": [new_category],
                                                                "Type": [type]})
                                                            st.session_state.table_data = pd.concat(
                                                                [st.session_state.table_data, new_entry], ignore_index=True)
                                                        delete_all(table_nm)
                                                        add_category_df(st.session_state.table_data, table_nm)
                                                        message_to_display = f"✅ Added: {new_category} - {keyword_list}"

                                            else:
                                                success_message = False
                                                message_to_display = "⚠ Please enter both Category and Keyword!"

                                    if message_to_display != "":
                                        if not success_message:
                                            st.error(message_to_display)
                                        else:
                                            st.success(message_to_display)
                                        message_to_display = ""
                                        time.sleep(2)
                                        refresh_page()

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
                                        height=600,
                                        fit_columns_on_grid_load=True
                                    )

                                    # Get selected rows as a DataFrame
                                    selected_rows = pd.DataFrame(grid_response["selected_rows"])

                                    # Delete Selected Rows
                                    if not selected_rows.empty and st.button("❌ Delete Selected Rows"):
                                        st.session_state.table_data = st.session_state.table_data.merge(selected_rows, how="left",
                                                                                                    indicator=True).query(
                                            '_merge == "left_only"').drop('_merge', axis=1)
                                        delete_all(table_nm)
                                        add_category_df(st.session_state.table_data, table_nm)
                                        time.sleep(2)
                                        refresh_page()

                                    # Handle Replace Prompt
                                    if st.session_state.replace_prompt:
                                        st.warning(
                                            f"⚠ The keyword **'{st.session_state.pending_keyword}'** already exists under **'{st.session_state.existing_category}'** category.")

                                        colA, colB = st.columns(2)

                                        if colA.button("🔄 Replace Existing"):
                                            st.session_state.table_data.loc[
                                                st.session_state.table_data["Keyword"] == st.session_state.pending_keyword, "Category"] = st.session_state.pending_category
                                            st.session_state.replace_prompt = False
                                            refresh_table()

                                        if colB.button("❌ Cancel"):
                                            st.session_state.replace_prompt = False
                                            refresh_table()
                                except Exception as e:
                                    st.toast(":red[Something went wrong.Please try again.]")
                                    time.sleep(2)
                                    refresh_page()

                            with tab7:
                                try:
                                    st.subheader("Pending Beta Requests")
                                    pending_users = fetch_pending_users()

                                    if pending_users:
                                        for user in pending_users:
                                            col1, col2, col3,clll4 = st.columns([4, 1.2, 1.2,3])
                                            col1.write(f"Name: {user['name']},\nEmail: {user['email']}")
                                            approve_button = col2.button("Approve", key=f"approve_{user['id']}")
                                            reject_button = col3.button("Reject", key=f"reject_{user['id']}")


                                            if approve_button:
                                                update_user_approval(user['id'], approve=True)
                                                subject=f"{user['name']} - Welcome to Fintellect"
                                                body=f"""
Hey {user['name']},

Welcome to Fintellect! 🎉 We're thrilled to have you on board as one of our early users.

Fintellect is built with a simple goal—to help you take control of your finances with clarity and ease. We're still in our early days, and your feedback will play a huge role in shaping the platform into something truly valuable.

Feel free to explore, and if you have any thoughts, suggestions, or even just want to say hi, we’d love to hear from you! Just hit reply or reach out anytime.

Thanks for being part of this journey with us. Let’s build something great together!

Cheers,
Team Fintellect
                                                """
                                                welcome_email(body,subject,user['email'])
                                                st.rerun()
                                            if reject_button:
                                                delete_user(user['id'])
                                                st.rerun()
                                    else:
                                        st.write("No pending requests.")

                                except Exception as e:
                                    print(f"Error in beta request : {e}")
                                    st.toast(":red[Something went wrong.Please try again.]")
                                    time.sleep(2)
                                    st.rerun()


                except Exception as e:
                    print(f"Error in fetching data : {e}")
                    st.toast(e)
                    # delete_data(db_name,user_name,"Name is NULL")
                    time.sleep(2)
                    refresh_page()
            elif app_name == "networth":
                if st.sidebar.button("Go to Main Page"):
                    main_page = True
                if main_page:
                    streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'nothing')", key="two")
                    # cookies.save()
                    app_name = "nothing"
                    time.sleep(1)
                    refresh_page()
                st.sidebar.write(f"<p style='margin-bottom: 5px;'>Logged in as {name}</p>", unsafe_allow_html=True)
                st.sidebar.markdown("---")
                networth(authenticator)
            else:
                # Main page content when no app is selected
                st.markdown("""
                                <style>
                                    .block-container {
                                        padding-top: 0rem !important;
                                    }
                                    [data-testid="stVerticalBlock"] {
                                        gap: 0.5rem !important;
                                    }
                                    .stMarkdown {
                                        margin-bottom: 0.5rem !important;
                                    }

                                </style>
                            """, unsafe_allow_html=True)

                st.write("# Welcome to Fintellect! 👋")
                st.markdown("""
                    ### Select an app to get started:
                """)
                
                # Create columns for app buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 20px;'>
                            <h3>🏦 Bank Statements Automation</h3>
                            <p>Upload and analyze your bank statements to track transactions and spending patterns.</p>
                            <div style='margin-top: 20px;'>
                    """, unsafe_allow_html=True)
                    if st.button("Open Bank Analyzer", key="bank_analyzer"):
                        streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'bank_statements')", key="bank_app")
                        time.sleep(1)
                        refresh_page()
                    st.markdown("</div></div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                        <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 20px;'>
                            <h3>📊 NetWorth App</h3>
                            <p>Track your assets, liabilities, and overall net worth over time.</p>
                            <div style='margin-top: 20px;'>
                    """, unsafe_allow_html=True)
                    if st.button("Open Net Worth Tracker", key="networth_tracker"):
                        streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'networth')", key="networth_app")
                        time.sleep(1)
                        refresh_page()
                    st.markdown("</div></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("""
                    <style>
                        .app-button {
                            width: 100%;
                            padding: 15px;
                            font-size: 16px;
                        }
                    </style>
                """, unsafe_allow_html=True)

        else:

            # Main page content when no app is selected
            st.markdown("""
                <style>
                    .block-container {
                        padding-top: 0rem !important;
                        margin-top: -2rem !important;
                    }
                    [data-testid="stVerticalBlock"] {
                        gap: 0rem !important;
                    }
                    .stMarkdown {
                        margin-bottom: 0rem !important;
                    }
                </style>
            """, 
            unsafe_allow_html=True)

            st.write("# Welcome to Fintellect! 👋")
            st.markdown("<br>", unsafe_allow_html=True)  # Added extra spacing below the title

            st.markdown("### Select an app to get started:")
            st.markdown("<br>", unsafe_allow_html=True)  # Added spacing below the subtitle

            # Create columns for app buttons
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                    <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 30px;'>
                        <h3>🏦 Bank Statements Analyzer</h3>
                        <p>Upload and analyze your bank statements to track transactions and spending patterns.</p>
                        <div style='margin-top: 30px;'>  <!-- Increased margin here -->
                """, unsafe_allow_html=True)
                
                if st.button("Open Bank Statements Analyzer", key="bank_analyzer"):
                    streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'bank_statements')", key="bank_app")
                    time.sleep(1)
                    refresh_page()

                st.markdown("</div></div>", unsafe_allow_html=True)

            with col2:
                st.markdown("""
                    <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 30px;'>
                        <h3>📊 Net Worth Tracker</h3>
                        <p>Monitor your assets, liabilities, and overall financial net worth consistently over time.</p>
                        <div style='margin-top: 30px;'>  <!-- Increased margin here -->
                """, unsafe_allow_html=True)
                
                if st.button("Open Net Worth Tracker", key="networth_tracker"):
                    streamlit_js_eval(js_expressions="localStorage.setItem('app_name', 'networth')", key="networth_app")
                    time.sleep(1)
                    refresh_page()
                
                st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown("---")

            # Sidebar dropdown to select an app
            st.sidebar.header("📂 Select an App")
            app_name = st.sidebar.selectbox("Choose below:", list(apps.keys()))
            app_name = apps[app_name]
            st.sidebar.markdown("<br>", unsafe_allow_html=True)  # Added space between dropdown and button

            if st.sidebar.button("Open app", use_container_width=True):
                streamlit_js_eval(js_expressions=f"localStorage.setItem('app_name', '{app_name}')", key="One")
                time.sleep(1)
                refresh_page()

            # Style Adjustments
            st.markdown("""
                <style>
                    .st-emotion-cache-1gwvy71 { padding-bottom: 0rem; }
                    .stButton>button { margin-top: 10px; }
                </style>
            """, unsafe_allow_html=True)

            # Sidebar spacing fix
            st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

            # Log out button
            st.sidebar.markdown("---")
            if st.sidebar.button("Log out", use_container_width=True):
                authenticator.logout()
  
    else:
        try:
            st.markdown(
                """
                <style>
                    div.block-container { padding-top: 0rem; } /* Reduce padding */
                    div[data-testid="stTabs"] { margin-top: -510px; } /* Move tabs higher */
                    .stButton>button { margin-top: -200px; } /* Move buttons lower */
                </style>
                """,
                unsafe_allow_html=True
            )
            if not user_status:
                if name:
                    page1()
                    if st.sidebar.button("Request for Beta Version", use_container_width=True):
                        insert_user(name, user_email)
                        st.toast(":green[✅ Request submitted successfully.]")
                        time.sleep(2)
                        refresh_page()
                else:
                    authenticator.logout()

            elif not user_status['is_approved']:
                page2()

            if st.sidebar.button("Log out", use_container_width=True):
                authenticator.logout()

        except Exception as e:
            print(f"Error in fetching data : {e}")
            st.toast(":red[Something went wrong.]")
            time.sleep(2)
            refresh_page()

  
else:
    st.cache_data.clear()
    streamlit_js_eval(js_expressions=f"localStorage.setItem('app_name', 'nothing')", key="One")
    auth_url = authenticator.login()
    if not auth_url:
        st.error("Authentication URL is not available.")
    else:
        css = """
                <style>
                    header[data-testid="stHeader"] {
                        z-index: 1000;
                    }

                    /* Button Wrapper */
                    .gcenter {
                        margin-top: 0.5rem; /* Reduced top margin */
                        height: 50px; /* Reduced height */
                        overflow-x: hidden;
                        width: 100%; /* Ensures it aligns with text width */
                        display: flex;
                        position: fixed;
                        top: 1.5vh; /* Adjusted height for better placement */
                        left: 4vw; /* Keeps alignment with text */
                        background-color: transparent; /* No background */
                        z-index: 1000000000000000;
                        justify-content: flex-start; /* Aligns with text */
                        align-items: center;
                    }

                    /* Google Button */
                    .google-button {
                        background-color: #4285F4;
                        color: white !important;
                        border-radius: 5px;
                        padding: 6px 12px; /* Reduced padding */
                        font-size: 1.2rem;
                        border: none;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        text-decoration: none !important;
                        gap: 6px;
                        box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.3);
                    }

                    .google-button img {
                        width: 1.3rem; /* Adjusted icon size */
                        height: 1.3rem;
                        margin-left: 4px;
                        border-radius: 50%;
                    }

                    /* Prevent Text Overlap */
                    .content {
                        margin-top: 4rem; /* Pushes content down */
                    }

                    /* Responsive Adjustments */
                    @media (max-width: 1100px) {
                        .gcenter {
                            left: 3vw; /* Align with text */
                            top: 1.5vh;
                            width: 100%;
                        }
                        .google-button {
                            padding: 5px 10px;
                            font-size: 1.1rem;
                        }
                    }

                    @media (max-width: 480px) {
                        .gcenter {
                            left: 2vw; /* Align with text */
                            top: 1.5vh;
                        }
                        .google-button {
                            padding: 4px 8px;
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