import streamlit as st
from datetime import datetime, date
from database import *
import pandas as pd
from utils import *
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder

def display_combined_aggrid(data, title):
    st.subheader(title)
    gb = GridOptionsBuilder.from_dataframe(data)
    # Set default column widths to reduce horizontal scrolling
    gb.configure_default_column(min_column_width=80, width=100)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=len(data))
    gridOptions = gb.build()
    # Auto-fit columns on load so that they appear perfect without clicking reset
    AgGrid(data, gridOptions=gridOptions, fit_columns_on_grid_load=True)

def create_combined_table(username):
    income_data = get_incomes(username)
    expense_data = get_expenses(username)
    investment_data = get_investments(username)
    savings_data = get_savings(username)
    
    # Build Income DataFrame
    df_income = pd.DataFrame(income_data, columns=["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"])
    df_income = df_income.rename(columns={"Source": "Type", "Growth_Rate": "Inflation / Growth Rate"})
    df_income["Category"] = "Income"
    
    # Build Expenses DataFrame
    df_expenses = pd.DataFrame(expense_data, columns=["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"])
    df_expenses = df_expenses.rename(columns={"Expense_Type": "Type", "Inflation_Rate": "Inflation / Growth Rate"})
    df_expenses["Category"] = "Expenses"
    
    # Build Investments DataFrame
    df_investments = pd.DataFrame(investment_data, columns=["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"])
    df_investments = df_investments.rename(columns={
        "Amount": "Value",
        "Start Date": "Start_Date",
        "End Date": "End_Date",
        "Rate of Return": "Inflation / Growth Rate"
    })
    df_investments["Frequency"] = None
    df_investments["Category"] = "Investments"
    
    # Build Savings DataFrame
    df_savings = pd.DataFrame(savings_data, columns=["ID", "Savings Rate"])
    df_savings["Category"] = "Savings Rate"
    for col in ["Type", "Value", "Frequency", "Start_Date", "End_Date"]:
        df_savings[col] = None
    df_savings = df_savings.rename(columns={"Savings Rate": "Inflation / Growth Rate"})
    
    # Convert date columns to formatted string in each DataFrame to remove time component
    for df in [df_income, df_expenses, df_investments]:
        for col in ["Start_Date", "End_Date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Combine all DataFrames into one and reorder columns
    combined_df = pd.concat([df_income, df_expenses, df_investments, df_savings], ignore_index=True)
    combined_df = combined_df[["Category", "Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation / Growth Rate"]]
    return combined_df

def display_combined_table(username):
    combined_df = create_combined_table(username)
    display_combined_aggrid(combined_df, "Combined Financial Data Table")

def calculate_age(dob):
    """Calculate age based on date of birth."""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def result():
    username = st.session_state.get("username")
    st.header("Net Worth Projection")
    st.markdown("Check all your inputs below. If you need to change anything or add/remove data, go to the respective tabs and add the details")
    
    # Display combined table at the top
    display_combined_table(username)
    
    # Retrieve and format Dependents Data
    dependents_data = get_dependents(username)
    dependents_columns = ["ID", "Name", "Date_of_Birth", "Gender", "Relationship"]
    df_dependents = pd.DataFrame(dependents_data, columns=dependents_columns)
    
    # Convert Date_of_Birth to datetime and calculate Age
    df_dependents["Date_of_Birth"] = pd.to_datetime(df_dependents["Date_of_Birth"], errors="coerce")
    df_dependents["Age"] = df_dependents["Date_of_Birth"].apply(calculate_age)
    
    # Format Date_of_Birth as string for display (remove time component)
    df_dependents["Date_of_Birth"] = df_dependents["Date_of_Birth"].dt.strftime("%Y-%m-%d")
    
    income_data = get_incomes(username)
    income_cols = ["ID", "Source", "Value", "Frequency", "Start_Date", "End_Date", "Growth_Rate"]
    df_incomes = pd.DataFrame(income_data, columns=income_cols)
    
    expense_data = get_expenses(username)
    expense_cols = ["ID", "Expense_Type", "Value", "Frequency", "Start_Date", "End_Date", "Inflation_Rate"]
    df_expenses = pd.DataFrame(expense_data, columns=expense_cols)
    
    investment_data = get_investments(username)
    savings_data = get_savings(username)
    
    # Convert investment data to DataFrame and format dates to remove time component
    columns = ["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"]
    df_investments = pd.DataFrame(investment_data, columns=columns)
    df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_investments["End Date"] = pd.to_datetime(df_investments["End Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_investments = df_investments.sort_values(by="End Date")
    
    # Convert date columns in income and expense DataFrames to formatted string (remove time component)
    df_incomes["Start_Date"] = pd.to_datetime(df_incomes["Start_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_incomes["End_Date"] = pd.to_datetime(df_incomes["End_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_expenses["Start_Date"] = pd.to_datetime(df_expenses["Start_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_expenses["End_Date"] = pd.to_datetime(df_expenses["End_Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    savings_rate = savings_data[0][1] if savings_data else "N/A"
    
    if st.button("Calculate Net Worth Projection"):
        # Convert to datetime format for calculations
        df_incomes["Start_Date"] = pd.to_datetime(df_incomes["Start_Date"], errors="coerce")
        df_incomes["End_Date"] = pd.to_datetime(df_incomes["End_Date"], errors="coerce")
        df_expenses["Start_Date"] = pd.to_datetime(df_expenses["Start_Date"], errors="coerce")
        df_expenses["End_Date"] = pd.to_datetime(df_expenses["End_Date"], errors="coerce")
        df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"], errors="coerce")
        df_investments["End Date"] = pd.to_datetime(df_investments["End Date"], errors="coerce")
        
        current_year = date.today().year
        dob = df_dependents[df_dependents["Relationship"] == "Self"]["Date_of_Birth"].values[0]
        dob = pd.to_datetime(dob).date()
        current_age = current_year - dob.year

        # Find the minimum start year across all datasets
        min_year = min(
            df_incomes["Start_Date"].dt.year.min(), 
            df_expenses["Start_Date"].dt.year.min(), 
            df_investments["Start Date"].dt.year.min()
        )
        future_years = range(min_year, current_year + (100 - current_age))  # Project till age 100

        net_worth = []
        income_details = []
        expense_details = []
        savings_details = []
        investment_details = []

        investible_savings = 0
        p, t = 0, 0  # Previous savings, previous net worth

        for year in future_years:
            annual_income = 0
            annual_expenses = 0
            annual_savings = 0
            annual_investment_income = 0
            net_ev = 0

            # Income Calculation
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

            # Expense Calculation
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

            # Compute Savings
            annual_savings = annual_income - annual_expenses
            temp_val = investible_savings if annual_savings > 0 else investible_savings + annual_savings
            sv_invest = max(temp_val, 0)
            income_from_sv = sv_invest * (savings_rate / 100) if sv_invest > 0 else 0
            investible_savings = max(annual_savings + sv_invest + income_from_sv, 0)

            savings_details.append({
                "Year": year, "Annual Savings / Deficit": annual_savings, 
                "Savings rate": savings_rate, "Starting Value - Investable Savings": sv_invest,
                "Income from Investable Savings": income_from_sv, 
                "EoY Savings Portfolio (Investable Savings)": investible_savings
            })

            # Investment Growth
            net_sv_ia, net_income_ia, net_ev = 0, 0, 0
            for _, row in df_investments.iterrows():
                if year < row["Start Date"].year:
                    continue  # Investment not yet started
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

            # Net Worth Calculation
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

        # Create DataFrames for display and download
        data = pd.DataFrame(net_worth)
        income_details_df = pd.DataFrame(income_details)
        expense_details_df = pd.DataFrame(expense_details)
        savings_details_df = pd.DataFrame(savings_details)
        investment_details_df = pd.DataFrame(investment_details)
        
        data = data.sort_values("Year")
        data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
        data["Age"] = pd.to_numeric(data["Age"], errors="coerce")
        data["Net Worth"] = pd.to_numeric(data["Net Worth"], errors="coerce")
        data = data.dropna().sort_values("Year").drop_duplicates(subset=["Year"])

        # Plot Net Worth Projection
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["Year"],
            y=data["Net Worth"],
            mode="lines+markers",
            name="Net Worth",
            line=dict(color="blue"),
            marker=dict(size=2)
        ))
        fig.add_trace(go.Scatter(
            x=[data["Year"].min(), data["Year"].max()],
            y=[0, 0],
            mode="lines",
            name="Baseline",
            line=dict(color="gray", dash="dash")
        ))
        negative_data = data[data["Net Worth"] < 0]
        if not negative_data.empty:
            fig.add_trace(go.Scatter(
                x=negative_data["Year"],
                y=negative_data["Net Worth"],
                fill="tozeroy",
                fillcolor="rgba(255, 0, 0, 0.3)",
                line=dict(color="rgba(255,0,0,0)"),
                showlegend=False
            ))
        year_min, year_max = int(data["Year"].min()), int(data["Year"].max())
        year_ticks = np.arange(year_min, year_max + 1, 5)
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

        # Offer Excel file download
        with BytesIO() as output:
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                data.to_excel(writer, sheet_name="Net Worth Projection", index=False)
                income_details_df.to_excel(writer, sheet_name="Income Details", index=False)
                expense_details_df.to_excel(writer, sheet_name="Expense Details", index=False)
                savings_details_df.to_excel(writer, sheet_name="Savings Details", index=False)
                investment_details_df.to_excel(writer, sheet_name="Investments & Assets Details", index=False)
            output.seek(0)
            st.download_button(
                label="Download Excel File",
                data=output,
                file_name="net_worth_projection.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    display_aggrid(df_dependents, "Dependents Data")
    display_aggrid(df_incomes, "Income Data")
    display_aggrid(df_expenses, "Expense Data")
    display_aggrid(df_investments, "Investments Data")
    
    st.subheader("Savings Rate")
    st.markdown(f"<p style='font-size: 18px;'>Savings rate: <b>{savings_rate}</b></p>", unsafe_allow_html=True)