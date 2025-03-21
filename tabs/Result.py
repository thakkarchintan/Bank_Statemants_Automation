# import streamlit as st
# from datetime import datetime, date
# from database import *
# import pandas as pd
# from utils import *
# import plotly.graph_objects as go
# from io import BytesIO
# import numpy as np
# from st_aggrid import AgGrid, GridOptionsBuilder
# import time

# def display_combined_aggrid(data):
#     # st.subheader(title)
#     gb = GridOptionsBuilder.from_dataframe(data)
#     row_height = 35  # Approximate height per row
#     calculated_height = (len(data)+2) * row_height
#     if "Age" in data.columns:
#         gb.configure_column("Age", cellStyle={"textAlign": "left"})
#     gridOptions = gb.build()
#     # Auto-fit columns on load so that they appear perfect without clicking reset
#     AgGrid(data, gridOptions=gridOptions, fit_columns_on_grid_load=True,height=calculated_height)

# def create_combined_table(username):
#     income_data = get_incomes(username)
#     expense_data = get_expenses(username)
#     investment_data = get_investments(username)
#     savings_data = get_savings(username)
    
#     # Build Income DataFrame
#     df_income = pd.DataFrame(income_data, columns=["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"])
#     df_income = df_income.drop(columns=["ID"]).rename(columns={
#         "Source": "Type", 
#         "Growth_Rate": "Inflation / Growth Rate",
#         "Start_Date": "Start Date",
#         "End_Date": "End Date"
#     })
#     df_income["Category"] = "Income"
    
#     # Build Expenses DataFrame
#     df_expenses = pd.DataFrame(expense_data, columns=["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"])
#     df_expenses = df_expenses.drop(columns=["ID"]).rename(columns={
#         "Expense_Type": "Type",
#         "Inflation_Rate": "Inflation / Growth Rate",
#         "Start_Date": "Start Date",
#         "End_Date": "End Date"
#     })
#     df_expenses["Category"] = "Expenses"
    
#     # Build Investments DataFrame
#     df_investments = pd.DataFrame(investment_data, columns=["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"])
#     df_investments = df_investments.drop(columns=["ID"]).rename(columns={
#         "Amount": "Value",
#         "Rate of Return": "Inflation / Growth Rate"
#     })
#     df_investments["Frequency"] = None
#     df_investments["Category"] = "Investments"
    
#     # Build Savings DataFrame
#     df_savings = pd.DataFrame(savings_data, columns=["ID", "Savings Rate"])
#     df_savings = df_savings.drop(columns=["ID"])
#     df_savings["Category"] = "Savings Rate"
#     for col in ["Type", "Value", "Frequency", "Start Date", "End Date"]:
#         df_savings[col] = None
#     df_savings = df_savings.rename(columns={"Savings Rate": "Inflation / Growth Rate"})
    
#     # Convert date columns to formatted strings
#     for df in [df_income, df_expenses, df_investments]:
#         for col in ["Start Date", "End Date"]:
#             if col in df.columns:
#                 df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    
#     # Combine and reorder columns
#     combined_df = pd.concat([df_income, df_expenses, df_investments, df_savings], ignore_index=True)
#     return combined_df[["Category", "Type", "Value", "Frequency", "Start Date", "End Date", "Inflation / Growth Rate"]]

# def display_combined_table(username):
#     combined_df = create_combined_table(username)
#     display_combined_aggrid(combined_df)

# def calculate_age(dob):
#     today = date.today()
#     return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# def result():
#     username = st.session_state.get("username")
#     # st.header("Net Worth Projection")
#     st.markdown("Check all your inputs below. If you need to change anything or add/remove data, go to the respective tabs and add the details")
    
#     display_combined_table(username)
    
#     # Dependents Data
#     dependents_data = get_dependents(username)
#     df_dependents = pd.DataFrame(dependents_data, columns=["ID", "Name", "Date of Birth", "Gender", "Relationship"])
#     df_dependents = df_dependents.drop(columns=["ID"])
#     df_dependents["Date of Birth"] = pd.to_datetime(df_dependents["Date of Birth"], errors="coerce")
#     df_dependents["Age"] = df_dependents["Date of Birth"].apply(calculate_age)
#     df_dependents["Date of Birth"] = df_dependents["Date of Birth"].dt.strftime("%Y-%m-%d")
    
#     if st.button("Calculate Net Worth Projection"):
#         income_data = get_incomes(username)
#         expense_data = get_expenses(username)
#         investment_data = get_investments(username)
#         savings_data = get_savings(username)
        
        
#         if not (income_data and expense_data and investment_data and savings_data):
#             st.toast("Please add the inputs to calculate net worth.", icon="⚠️")
#             time.sleep(3)  # Toast duration (adjust as needed)
#         else :
#             # Create DataFrames with ID columns removed
#             df_incomes = pd.DataFrame(income_data, columns=["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"]).drop(columns=["ID"])
#             df_expenses = pd.DataFrame(expense_data, columns=["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"]).drop(columns=["ID"])
#             df_investments = pd.DataFrame(investment_data, columns=["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"]).drop(columns=["ID"])
            
#             # Date conversions
#             df_incomes["Start_Date"] = pd.to_datetime(df_incomes["Start_Date"], errors="coerce")
#             df_incomes["End_Date"] = pd.to_datetime(df_incomes["End_Date"], errors="coerce")
#             df_expenses["Start_Date"] = pd.to_datetime(df_expenses["Start_Date"], errors="coerce")
#             df_expenses["End_Date"] = pd.to_datetime(df_expenses["End_Date"], errors="coerce")
#             df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"], errors="coerce")
#             df_investments["End Date"] = pd.to_datetime(df_investments["End Date"], errors="coerce")
            
#             # Calculation logic (same as original)
#             current_year = date.today().year
#             dob = df_dependents[df_dependents["Relationship"] == "Self"]["Date of Birth"].values[0]
#             dob = pd.to_datetime(dob).date()
#             current_age = current_year - dob.year

#             min_year = min(
#                 df_incomes["Start_Date"].dt.year.min(), 
#                 df_expenses["Start_Date"].dt.year.min(), 
#                 df_investments["Start Date"].dt.year.min()
#             )
#             future_years = range(min_year, current_year + (100 - current_age))

#             net_worth = []
#             income_details = []
#             expense_details = []
#             savings_details = []
#             investment_details = []

#             investible_savings = 0
#             p, t = 0, 0

#             for year in future_years:
#                 annual_income = 0
#                 annual_expenses = 0
#                 annual_savings = 0
#                 annual_investment_income = 0
#                 net_ev = 0

#                 # Income calculation
#                 for _, row in df_incomes.iterrows():
#                     if row["Start_Date"].year <= year <= row["End_Date"].year:
#                         years_passed = year - row["Start_Date"].year
#                         annual_value = compute_annual_amount(row["Value"], row["Frequency"])
#                         annual_value = apply_growth_rate(annual_value, row["Growth_Rate"], years_passed)
#                         annual_income += annual_value
#                         income_details.append({
#                             "Year": year, "Source": row["Source"], "Value": row["Value"], 
#                             "Frequency": row["Frequency"], "Growth Rate (%)": row["Growth_Rate"], 
#                             "Annual Income": annual_value
#                         })

#                 # Expense calculation
#                 for _, row in df_expenses.iterrows():
#                     if row["Start_Date"].year <= year <= row["End_Date"].year:
#                         years_passed = year - row["Start_Date"].year
#                         annual_value = compute_annual_amount(row["Value"], row["Frequency"])
#                         annual_value = apply_growth_rate(annual_value, row["Inflation_Rate"], years_passed)
#                         annual_expenses += annual_value
#                         expense_details.append({
#                             "Year": year, "Type": row["Expense_Type"], "Value": row["Value"], 
#                             "Frequency": row["Frequency"], "Inflation Rate (%)": row["Inflation_Rate"], 
#                             "Annual Expense": annual_value
#                         })

#                 # Savings calculation
#                 annual_savings = annual_income - annual_expenses
#                 temp_val = investible_savings if annual_savings > 0 else investible_savings + annual_savings
#                 sv_invest = max(temp_val, 0)
#                 income_from_sv = sv_invest * (savings_data[0][1] / 100) if sv_invest > 0 else 0
#                 investible_savings = max(annual_savings + sv_invest + income_from_sv, 0)
#                 savings_details.append({
#                     "Year": year, "Annual Savings / Deficit": annual_savings, 
#                     "Savings rate": savings_data[0][1], "Starting Value - Investable Savings": sv_invest,
#                     "Income from Investable Savings": income_from_sv, 
#                     "EoY Savings Portfolio (Investable Savings)": investible_savings
#                 })

#                 # Investment calculation
#                 net_sv_ia, net_income_ia, net_ev = 0, 0, 0
#                 for _, row in df_investments.iterrows():
#                     if year < row["Start Date"].year:
#                         continue
#                     elif year == row["Start Date"].year:
#                         sv_ia = row["Amount"]
#                         income_ia = sv_ia * (row["Rate of Return"] / 100)
#                         ev = sv_ia + income_ia
#                     elif year <= row["End Date"].year:
#                         temp_val2 = ev + annual_savings if investible_savings == 0 and annual_savings < 0 else ev
#                         sv_ia = max(temp_val2, 0)
#                         income_ia = sv_ia * (row["Rate of Return"] / 100)
#                         ev = sv_ia + income_ia
#                     else:
#                         sv_ia, income_ia, ev = 0, 0, 0

#                     net_sv_ia += sv_ia
#                     net_income_ia += income_ia
#                     net_ev += ev
#                     investment_details.append({
#                         "Year": year, "Investment Type": row["Type"], 
#                         "Starting Value - Investments & Assets": sv_ia, 
#                         "Rate of Return (%)": row["Rate of Return"], 
#                         "Income from Investments & Assets": income_ia, 
#                         "Ending Value - Investments & Assets": ev
#                     })

#                 # Net worth calculation
#                 net_worth_val = (annual_savings + t if investible_savings == 0 and net_ev == 0 else net_ev + investible_savings) + (p if investible_savings == 0 else 0)
#                 p, t = investible_savings, net_worth_val
#                 net_worth.append({
#                     "Year": year, "Age": current_age + (year - current_year),
#                     "Income": annual_income, "Expenses": annual_expenses,
#                     "Annual Savings / Deficit": annual_savings,
#                     "Starting Value - Investable Savings": sv_invest,
#                     "Income from Investable Savings": income_from_sv,
#                     "EoY Savings Portfolio (Investable Savings)": investible_savings,
#                     "Starting Value - Investments & Assets": net_sv_ia,
#                     "Income from Investments & Assets": net_income_ia,
#                     "Ending Value - Investments & Assets": net_ev,
#                     "Net Worth": net_worth_val
#                 })

#             # Create DataFrames
#             data = pd.DataFrame(net_worth)
#             income_details_df = pd.DataFrame(income_details)
#             expense_details_df = pd.DataFrame(expense_details)
#             savings_details_df = pd.DataFrame(savings_details)
#             investment_details_df = pd.DataFrame(investment_details)
            
#             # Data processing
#             data = data.sort_values("Year").drop_duplicates(subset=["Year"])
#             data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
#             data["Age"] = pd.to_numeric(data["Age"], errors="coerce")
#             data["Net Worth"] = pd.to_numeric(data["Net Worth"], errors="coerce")
#             data = data.dropna()

#             # Visualization
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(
#                 x=data["Year"], y=data["Net Worth"], mode="lines+markers",
#                 name="Net Worth", line=dict(color="blue"), marker=dict(size=2)
#             ))
#             fig.add_trace(go.Scatter(
#                 x=[data["Year"].min(), data["Year"].max()], y=[0, 0],
#                 mode="lines", name="Baseline", line=dict(color="gray", dash="dash")
#             ))
#             negative_data = data[data["Net Worth"] < 0]
#             if not negative_data.empty:
#                 fig.add_trace(go.Scatter(
#                     x=negative_data["Year"], y=negative_data["Net Worth"],
#                     fill="tozeroy", fillcolor="rgba(255, 0, 0, 0.3)",
#                     line=dict(color="rgba(255,0,0,0)"), showlegend=False
#                 ))
#             year_ticks = np.arange(int(data["Year"].min()), int(data["Year"].max()) + 1, 5)
#             age_ticks = np.interp(year_ticks, data["Year"], data["Age"]).astype(str)
#             fig.update_layout(
#                 xaxis=dict(
#                     title="Year",
#                     tickmode="array",
#                     tickvals=year_ticks,
#                     ticktext=[str(y) for y in year_ticks]
#                 ),
#                 xaxis2=dict(
#                     title="Age",
#                     overlaying="x",
#                     side="top",
#                     tickmode="array",
#                     tickvals=year_ticks,
#                     ticktext=[str(a) for a in age_ticks]
#                 ),
#                 yaxis=dict(title="Net Worth"),
#                 legend=dict(x=0, y=1),
#             )
#             st.plotly_chart(fig)

#             # Excel export
#             with BytesIO() as output:
#                 with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#                     data.to_excel(writer, sheet_name="Net Worth Projection", index=False)
#                     income_details_df.to_excel(writer, sheet_name="Income Details", index=False)
#                     expense_details_df.to_excel(writer, sheet_name="Expense Details", index=False)
#                     savings_details_df.to_excel(writer, sheet_name="Savings Details", index=False)
#                     investment_details_df.to_excel(writer, sheet_name="Investments Details", index=False)
#                 output.seek(0)
#                 st.download_button(
#                     label="Download Excel File",
#                     data=output,
#                     file_name="net_worth_projection.xlsx",
#                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 )

#     # Display only dependents table
#     st.subheader("Dependents Data")
#     row_height = 35  # Approximate height per row
#     calculated_height = (len(df_dependents)+2) * row_height
#     AgGrid(df_dependents, fit_columns_on_grid_load=True,height=calculated_height)









import streamlit as st
from datetime import datetime, date
from database import *
import pandas as pd
from utils import *
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import time

def display_combined_aggrid(data):
    # st.subheader(title)
    gb = GridOptionsBuilder.from_dataframe(data)
    row_height = 35  # Approximate height per row
    calculated_height = (len(data)+2) * row_height
    if "Age" in data.columns:
        gb.configure_column("Age", cellStyle={"textAlign": "left"})
    gridOptions = gb.build()
    # Auto-fit columns on load so that they appear perfect without clicking reset
    AgGrid(data, gridOptions=gridOptions, fit_columns_on_grid_load=True,height=calculated_height)

def create_combined_table(username):
    income_data = get_incomes(username)
    expense_data = get_expenses(username)
    investment_data = get_investments(username)
    savings_data = get_savings(username)
    
    # Build Income DataFrame
    df_income = pd.DataFrame(income_data, columns=["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"])
    df_income = df_income.drop(columns=["ID"]).rename(columns={
        "Source": "Type", 
        "Growth_Rate": "Inflation / Growth Rate",
        "Start_Date": "Start Date",
        "End_Date": "End Date"
    })
    df_income["Category"] = "Income"
    
    # Build Expenses DataFrame
    df_expenses = pd.DataFrame(expense_data, columns=["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"])
    df_expenses = df_expenses.drop(columns=["ID"]).rename(columns={
        "Expense_Type": "Type",
        "Inflation_Rate": "Inflation / Growth Rate",
        "Start_Date": "Start Date",
        "End_Date": "End Date"
    })
    df_expenses["Category"] = "Expenses"
    
    # Build Investments DataFrame
    df_investments = pd.DataFrame(investment_data, columns=["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"])
    df_investments = df_investments.drop(columns=["ID"]).rename(columns={
        "Amount": "Value",
        "Rate of Return": "Inflation / Growth Rate"
    })
    df_investments["Frequency"] = None
    df_investments["Category"] = "Investments"
    
    # Build Savings DataFrame
    df_savings = pd.DataFrame(savings_data, columns=["ID", "Savings Rate"])
    df_savings = df_savings.drop(columns=["ID"])
    df_savings["Category"] = "Savings Rate"
    for col in ["Type", "Value", "Frequency", "Start Date", "End Date"]:
        df_savings[col] = None
    df_savings = df_savings.rename(columns={"Savings Rate": "Inflation / Growth Rate"})
    
    # Convert date columns to formatted strings
    for df in [df_income, df_expenses, df_investments]:
        for col in ["Start Date", "End Date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Combine and reorder columns
    combined_df = pd.concat([df_income, df_expenses, df_investments, df_savings], ignore_index=True)
    return combined_df[["Category", "Type", "Value", "Frequency", "Start Date", "End Date", "Inflation / Growth Rate"]]

def display_combined_table(username):
    combined_df = create_combined_table(username)
    display_combined_aggrid(combined_df)

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def result():
    username = st.session_state.get("username")
    st.header("Net Worth Projection")
    st.markdown("Check all your inputs below. If you need to change anything or add/remove data, go to the respective tabs and add the details")
    
    display_combined_table(username)
    
    # Dependents Data
    dependents_data = get_dependents(username)
    df_dependents = pd.DataFrame(dependents_data, columns=["ID", "Name", "Date_of_Birth", "Gender", "Relationship"])
    df_dependents = df_dependents.drop(columns=["ID"])
    df_dependents["Date_of_Birth"] = pd.to_datetime(df_dependents["Date_of_Birth"], errors="coerce")
    df_dependents["Age"] = df_dependents["Date_of_Birth"].apply(calculate_age)
    df_dependents["Date_of_Birth"] = df_dependents["Date_of_Birth"].dt.strftime("%Y-%m-%d")
    
    if st.button("Calculate Net Worth Projection"):
        income_data = get_incomes(username)
        expense_data = get_expenses(username)
        investment_data = get_investments(username)
        savings_data = get_savings(username)
        
        
        if not (income_data and expense_data and investment_data and savings_data):
            st.toast("Please add the inputs to calculate net worth.", icon="⚠️")
            time.sleep(3)  # Toast duration (adjust as needed)
        else :
            # Create DataFrames with ID columns removed
            df_incomes = pd.DataFrame(income_data, columns=["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"]).drop(columns=["ID"])
            df_expenses = pd.DataFrame(expense_data, columns=["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"]).drop(columns=["ID"])
            df_investments = pd.DataFrame(investment_data, columns=["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"]).drop(columns=["ID"])
            
            # Date conversions
            df_incomes["Start_Date"] = pd.to_datetime(df_incomes["Start_Date"], errors="coerce")
            df_incomes["End_Date"] = pd.to_datetime(df_incomes["End_Date"], errors="coerce")
            df_expenses["Start_Date"] = pd.to_datetime(df_expenses["Start_Date"], errors="coerce")
            df_expenses["End_Date"] = pd.to_datetime(df_expenses["End_Date"], errors="coerce")
            df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"], errors="coerce")
            df_investments["End Date"] = pd.to_datetime(df_investments["End Date"], errors="coerce")
            
            # Calculation logic (same as original)
            current_year = date.today().year
            dob = df_dependents[df_dependents["Relationship"] == "Self"]["Date_of_Birth"].values[0]
            dob = pd.to_datetime(dob).date()
            current_age = current_year - dob.year

            min_year = min(
                df_incomes["Start_Date"].dt.year.min(), 
                df_expenses["Start_Date"].dt.year.min(), 
                df_investments["Start Date"].dt.year.min()
            )
            future_years = range(min_year, current_year + (100 - current_age))

            net_worth = []
            income_details = []
            expense_details = []
            savings_details = []
            investment_details = []

            investible_savings = 0
            p, t = 0, 0

            for year in future_years:
                annual_income = 0
                annual_expenses = 0
                annual_savings = 0
                annual_investment_income = 0
                net_ev = 0

                # Income calculation
                for _, row in df_incomes.iterrows():
                    if row["Start_Date"].year <= year <= row["End_Date"].year:
                        years_passed = year - row["Start_Date"].year
                        annual_value = compute_annual_amount(row["Value"], row["Frequency"])
                        annual_value = apply_growth_rate(annual_value, row["Growth_Rate"], years_passed)
                        annual_income += annual_value
                        income_details.append({
                            "Year": year, "Source": row["Source"], "Value": row["Value"], 
                            "Frequency": row["Frequency"], "Growth Rate (%)": row["Growth_Rate"], 
                            "Annual Income": annual_value
                        })

                # Expense calculation
                for _, row in df_expenses.iterrows():
                    if row["Start_Date"].year <= year <= row["End_Date"].year:
                        years_passed = year - row["Start_Date"].year
                        annual_value = compute_annual_amount(row["Value"], row["Frequency"])
                        annual_value = apply_growth_rate(annual_value, row["Inflation_Rate"], years_passed)
                        annual_expenses += annual_value
                        expense_details.append({
                            "Year": year, "Type": row["Expense_Type"], "Value": row["Value"], 
                            "Frequency": row["Frequency"], "Inflation Rate (%)": row["Inflation_Rate"], 
                            "Annual Expense": annual_value
                        })

                # Savings calculation
                annual_savings = annual_income - annual_expenses
                temp_val = investible_savings if annual_savings > 0 else investible_savings + annual_savings
                sv_invest = max(temp_val, 0)
                income_from_sv = sv_invest * (savings_data[0][1] / 100) if sv_invest > 0 else 0
                investible_savings = max(annual_savings + sv_invest + income_from_sv, 0)
                savings_details.append({
                    "Year": year, "Annual Savings / Deficit": annual_savings, 
                    "Savings rate": savings_data[0][1], "Starting Value - Investable Savings": sv_invest,
                    "Income from Investable Savings": income_from_sv, 
                    "EoY Savings Portfolio (Investable Savings)": investible_savings
                })

                # Investment calculation
                net_sv_ia, net_income_ia, net_ev = 0, 0, 0
                for _, row in df_investments.iterrows():
                    if year < row["Start Date"].year:
                        continue
                    elif year == row["Start Date"].year:
                        sv_ia = row["Amount"]
                        income_ia = sv_ia * (row["Rate of Return"] / 100)
                        ev = sv_ia + income_ia
                    elif year <= row["End Date"].year:
                        temp_val2 = ev + annual_savings if investible_savings == 0 and annual_savings < 0 else ev
                        sv_ia = max(temp_val2, 0)
                        income_ia = sv_ia * (row["Rate of Return"] / 100)
                        ev = sv_ia + income_ia
                    else:
                        sv_ia, income_ia, ev = 0, 0, 0

                    net_sv_ia += sv_ia
                    net_income_ia += income_ia
                    net_ev += ev
                    investment_details.append({
                        "Year": year, "Investment Type": row["Type"], 
                        "Starting Value - Investments & Assets": sv_ia, 
                        "Rate of Return (%)": row["Rate of Return"], 
                        "Income from Investments & Assets": income_ia, 
                        "Ending Value - Investments & Assets": ev
                    })

                # Net worth calculation
                net_worth_val = (annual_savings + t if investible_savings == 0 and net_ev == 0 else net_ev + investible_savings) + (p if investible_savings == 0 else 0)
                p, t = investible_savings, net_worth_val
                net_worth.append({
                    "Year": year, "Age": current_age + (year - current_year),
                    "Income": annual_income, "Expenses": annual_expenses,
                    "Annual Savings / Deficit": annual_savings,
                    "Starting Value - Investable Savings": sv_invest,
                    "Income from Investable Savings": income_from_sv,
                    "EoY Savings Portfolio (Investable Savings)": investible_savings,
                    "Starting Value - Investments & Assets": net_sv_ia,
                    "Income from Investments & Assets": net_income_ia,
                    "Ending Value - Investments & Assets": net_ev,
                    "Net Worth": net_worth_val
                })

            # Create DataFrames
            data = pd.DataFrame(net_worth)
            income_details_df = pd.DataFrame(income_details)
            expense_details_df = pd.DataFrame(expense_details)
            savings_details_df = pd.DataFrame(savings_details)
            investment_details_df = pd.DataFrame(investment_details)
            
            # Data processing
            data = data.sort_values("Year").drop_duplicates(subset=["Year"])
            data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
            data["Age"] = pd.to_numeric(data["Age"], errors="coerce")
            data["Net Worth"] = pd.to_numeric(data["Net Worth"], errors="coerce")
            data = data.dropna()

            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data["Year"], y=data["Net Worth"], mode="lines+markers",
                name="Net Worth", line=dict(color="blue"), marker=dict(size=2)
            ))
            fig.add_trace(go.Scatter(
                x=[data["Year"].min(), data["Year"].max()], y=[0, 0],
                mode="lines", name="Baseline", line=dict(color="gray", dash="dash")
            ))
            negative_data = data[data["Net Worth"] < 0]
            if not negative_data.empty:
                fig.add_trace(go.Scatter(
                    x=negative_data["Year"], y=negative_data["Net Worth"],
                    fill="tozeroy", fillcolor="rgba(255, 0, 0, 0.3)",
                    line=dict(color="rgba(255,0,0,0)"), showlegend=False
                ))
            year_ticks = np.arange(int(data["Year"].min()), int(data["Year"].max()) + 1, 5)
            age_ticks = np.interp(year_ticks, data["Year"], data["Age"]).astype(str)
            fig.update_layout(
                xaxis=dict(
                    title="Year",
                    tickmode="array",
                    tickvals=year_ticks,
                    ticktext=[str(y) for y in year_ticks]
                ),
                xaxis2=dict(
                    title="Age",
                    overlaying="x",
                    side="top",
                    tickmode="array",
                    tickvals=year_ticks,
                    ticktext=[str(a) for a in age_ticks]
                ),
                yaxis=dict(title="Net Worth"),
                legend=dict(x=0, y=1),
            )
            st.plotly_chart(fig)

            # Excel export
            with BytesIO() as output:
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    data.to_excel(writer, sheet_name="Net Worth Projection", index=False)
                    income_details_df.to_excel(writer, sheet_name="Income Details", index=False)
                    expense_details_df.to_excel(writer, sheet_name="Expense Details", index=False)
                    savings_details_df.to_excel(writer, sheet_name="Savings Details", index=False)
                    investment_details_df.to_excel(writer, sheet_name="Investments Details", index=False)
                output.seek(0)
                st.download_button(
                    label="Download Excel File",
                    data=output,
                    file_name="net_worth_projection.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # Display only dependents table
    st.subheader("Dependents Data")
    row_height = 35  # Approximate height per row
    calculated_height = (len(df_dependents)+2) * row_height
    df_dependents = rename_column(df_dependents,"Date_of_Birth","Date of Birth")
    AgGrid(df_dependents, fit_columns_on_grid_load=True,height=calculated_height)