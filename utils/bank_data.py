admins = ['professionalbuzz','shirishkumar1949','abutalha11503','ronakmehta0709','nikita__d@ambers']

bank_status_dict = {
    'Axis Bank': False,
    'HDFC Bank': False,
    'State Bank of India': False,
    'ICICI Bank': False,
    'Bank of Baroda': False,
    'Bank of India': False,
    'Indian Overseas Bank': False,

    'Bandhan Bank': True,
    'Kotak Bank': False,

    'Union Bank of India': False,
    'Punjab National Bank': False,
    'Canara Bank': False,
    'IndusInd Bank': False,
    'Indian Bank': False,
    'IDBI': False,
    'Yes Bank': False,
    'IDFC FIRST Bank': False,
    'Federal Bank': False,
    'Central Bank of India': False,
    'Bank of Maharashtra': False,
    'UCO Bank': False,
    'RBL Bank': False,
    'Jammu & Kashmir Bank': False,
    'Karnataka Bank': False,
    'Karur Vysya Bank': False
}

bank_list = [
    "HDFC Bank",
    "State Bank of India",
    "ICICI Bank",
    "Bank of Baroda",
    "Bank of India",
    "Indian Overseas Bank",

    "Bandhan Bank",
    "Kotak Bank",

    "Axis Bank",
    # "Union Bank of India",
    # "Punjab National Bank",
    # "Canara Bank",
    # "IndusInd Bank",
    # "Indian Bank",
    # "IDBI",
    # "Yes Bank",
    # "IDFC FIRST Bank",
    # "Federal Bank",
    # "Central Bank of India",
    # "Bank of Maharashtra",
    # "UCO Bank",
    # "RBL Bank",
    # "Jammu & Kashmir Bank",
    # "Karnataka Bank",
    # "Karur Vysya Bank"
]

table_columns_dic = {
    'HDFC Bank': ['Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.','Closing Balance'],
    'State Bank of India': ['Date', 'Details', 'Debit', 'Credit','Balance'],
    'ICICI Bank': ['Transaction Date','Transaction Remarks','Withdrawal Amount (INR )','Deposit Amount (INR )','Balance (INR )'],
    'Bank of Baroda': ['TRAN DATE', 'NARRATION', 'WITHDRAWAL(DR)', 'DEPOSIT(CR)','BALANCE(INR)'],
    'Bank of India': ['Date','Remarks','Debit','Credit','Balance Amount'],
    'Indian Overseas Bank': ['DATE','NARATION','DEBIT','CREDIT','BALANCE'],
    
    'Bandhan Bank': ['Transaction Date','Description','Amount (INR)','Cr/Dr','Balance'],
    'Kotak Bank': ['Transaction Date','Description','Amount','Dr / Cr','Balance'],

    'Axis Bank': ["Tran Date","PARTICULARS","DR","CR","BAL"],
    'Union Bank of India': [],
    'Punjab National Bank': [],
    'Canara Bank': [],
    'IndusInd Bank': [],
    'Indian Bank': [],
    'IDBI': [],
    'Yes Bank': [],
    'IDFC FIRST Bank': [],
    'Federal Bank': [],
    'Central Bank of India': [],
    'Bank of Maharashtra': [],
    'UCO Bank': [],
    'RBL Bank': [],
    'Jammu & Kashmir Bank': [],
    'Karnataka Bank': [],
    'Karur Vysya Bank': []
}

table_columns_pdf_dic = {
    'HDFC Bank': ['Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.','Closing Balance'],
    'State Bank of India': ['Date', 'Details', 'Debit', 'Credit','Balance'],
    'ICICI Bank': ['Transaction Date','Transaction Remarks','Withdrawal Amount\n(INR )', 'Deposit Amount\n(INR )','Balance (INR )'],
    'Bank of Baroda': ['TRAN DATE', 'NARRATION', 'WITHDRAWAL(DR)', 'DEPOSIT(CR)','BALANCE(INR)'],
    'Bank of India': ['Date','Remarks','Debit','Credit','Balance Amount'],
    'Indian Overseas Bank': ['DATE','NARATION','DEBIT','CREDIT','BALANCE'],
    
    'Bandhan Bank': ['Transaction Date','Description','Amount','Dr / Cr','Balance'],
                    #  ['Transaction Date','Description','Amount','Cr/Dr']],
    'Kotak Bank': 
    # ['TRANSACTION DATE','TRANSACTION DETAILS','BALANCE(₹)','DEBIT/CREDIT(₹)'],
    ['Date', 'Narration', 'Withdrawal(Dr)', 'Deposit(Cr)','Balance'],

    'Axis Bank': ["Tran Date", "Particulars", "Debit", "Credit","Balance"],
    'Union Bank of India': [],
    'Punjab National Bank': [],
    'Canara Bank': [],
    'IndusInd Bank': [],
    'Indian Bank': [],
    'IDBI': [],
    'Yes Bank': [],
    'IDFC FIRST Bank': [],
    'Federal Bank': [],
    'Central Bank of India': [],
    'Bank of Maharashtra': [],
    'UCO Bank': [],
    'RBL Bank': [],
    'Jammu & Kashmir Bank': [],
    'Karnataka Bank': [],
    'Karur Vysya Bank': []
}

banks_date_format = {
    "HDFC Bank": "%d/%m/%y",
    "State Bank of India": None,
    # "%d-%b-%Y",
    "ICICI Bank": "%d/%m/%Y",
    "Bank of Baroda": "%d/%m/%Y",
    "Bank of India": None,
    # "%d-%m-%Y",
    "Indian Overseas Bank": None,
    # "%d-%m-%Y",

    "Bandhan Bank": None,
    # "%d-%m-%Y",
    "Kotak Bank": None,
    # "%d/%m/%Y",

    "Axis Bank": "%d-%m-%Y",
    "Union Bank of India": "%d/%m/%Y",
    "Punjab National Bank": "%d/%m/%Y",
    "Canara Bank": "%d/%m/%Y",
    "IndusInd Bank": "%d/%m/%Y",
    "Indian Bank": "%d/%m/%Y",
    "IDBI": "%d/%m/%Y",
    "Yes Bank": "%d/%m/%Y",
    "IDFC FIRST Bank": "%d/%m/%Y",
    "Federal Bank": "%d/%m/%Y",
    "Central Bank of India": "%d/%m/%Y",
    "Bank of Maharashtra": "%d/%m/%Y",
    "UCO Bank": "%d/%m/%Y",
    "RBL Bank": "%d/%m/%Y",
    "Jammu & Kashmir Bank": "%d/%m/%Y",
    "Karnataka Bank": "%d/%m/%Y",
    "Karur Vysya Bank": "%d/%m/%Y"
}


    # 'df1': '%d/%m/%Y',  # dd/mm/yyyy
    # 'df2': '%d-%m-%Y',  # dd-mm-yyyy
    # 'df3': '%m/%d/%Y',  # mm/dd/yyyy
    # 'df4': '%m-%d-%Y',  # mm-dd-yyyy
    # 'df5': '%d-%b-%Y',  # dd-MMM-yyyy (e.g., 13-Jan-2025)
