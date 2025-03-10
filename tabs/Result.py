import streamlit as st
from datetime import datetime, date
from database import *
import pandas as pd
from utils import *
import plotly.graph_objects as go
from io import BytesIO
import numpy as np

def result() :
    username = st.session_state.get("username")
    st.header("Net Worth Projection")
    st.markdown("Check all your inputs below. If you need to change anything or add/remove data, go to the respective tabs and add the details")
    
    dependents_data = get_dependents(username)
    dependents_columns = ["ID","Name", "Date_of_Birth", "Gender", "Relationship"]
    df_dependents = pd.DataFrame(dependents_data, columns=dependents_columns)
    
    income_data = get_incomes(username)
    income_cols = ["ID","Source", "Value", "Frequency", "Start_Date" , "End_Date" , "Growth_Rate"]
    df_incomes=pd.DataFrame(income_data, columns=income_cols)
    
    expense_data = get_expenses(username)
    expense_cols = ["ID","Expense_Type", "Value", "Frequency", "Start_Date" , "End_Date" , "Inflation_Rate"]
    df_expenses=pd.DataFrame(expense_data, columns=expense_cols)
    
    investment_data = get_investments(username)
    savings_data = get_savings(username)
    
    # Convert investment data to DataFrame
    columns = ["ID", "Type", "Amount", "Start Date", "End Date", "Rate of Return"]
    df_investments = pd.DataFrame(investment_data, columns=columns)

    # Convert dates to datetime format
    df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"]).dt.date
    df_investments["End Date"] = pd.to_datetime(df_investments["End Date"]).dt.date

    # Sort investments by 'End Date' year
    df_investments = df_investments.sort_values(by="End Date")

    savings_rate = savings_data[0][1] if savings_data else "N/A"
    
        # Apply date formatting
    df_dependents = format_date_columns(df_dependents, ["Date_of_Birth"])
    df_incomes = format_date_columns(df_incomes, ["Start_Date", "End_Date"])
    df_expenses = format_date_columns(df_expenses, ["Start_Date", "End_Date"])
    df_investments = format_date_columns(df_investments, ["Start Date", "End Date"])
    
    display_aggrid(df_dependents, "Dependents Data")
    display_aggrid(df_incomes, "Income Data")
    display_aggrid(df_expenses, "Expense Data")
    display_aggrid(df_investments, "Investments Data")
    
    st.subheader("Savings Rate")
    st.markdown(f"<p style='font-size: 18px;'>Savings rate: <b>{savings_rate}</b></p>", unsafe_allow_html=True)
  
    
   
    if st.button("Calculate Net Worth Projection"):
        # Convert to datetime format
        df_incomes["Start_Date"] = pd.to_datetime(df_incomes["Start_Date"], errors="coerce")
        df_expenses["Start_Date"] = pd.to_datetime(df_expenses["Start_Date"], errors="coerce")
        df_investments["Start Date"] = pd.to_datetime(df_investments["Start Date"], errors="coerce")
        current_year = date.today().year
        dob = df_dependents[df_dependents["Relationship"] == "Self"]["Date_of_Birth"].values[0]
        dob = pd.to_datetime(dob).date()
        current_age = current_year - dob.year

        # Find the minimum start year across all datasets
        min_year = min(df_incomes["Start_Date"].dt.year.min(), df_expenses["Start_Date"].dt.year.min(), df_investments["Start Date"].dt.year.min())
        future_years = range(min_year, current_year + (100 - current_age))  # Project till age 100

        # Initialize results
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

        # Create DataFrames
        data = pd.DataFrame(net_worth)
        income_details_df = pd.DataFrame(income_details)
        expense_details_df = pd.DataFrame(expense_details)
        savings_details_df = pd.DataFrame(savings_details)
        investment_details_df = pd.DataFrame(investment_details)
        
        data = data.sort_values("Year")

            # Ensure 'Year' and 'Age' are numeric
        data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
        data["Age"] = pd.to_numeric(data["Age"], errors="coerce")
        data["Net Worth"] = pd.to_numeric(data["Net Worth"], errors="coerce")

        # Remove NaN values, sort, and drop duplicate years
        data = data.dropna().sort_values("Year").drop_duplicates(subset=["Year"])

        # -------------------------------
        # Create Plot with Dual X-Axes
        # -------------------------------
        fig = go.Figure()

        # Plot Net Worth as lines with markers
        fig.add_trace(go.Scatter(
            x=data["Year"],
            y=data["Net Worth"],
            mode="lines+markers",
            name="Net Worth",
            line=dict(color="blue"),
            
            marker=dict(size=2)  # Reduce marker size to make dots less prominent

        ))

        # Add a horizontal dashed baseline at y=0
        fig.add_trace(go.Scatter(
            x=[data["Year"].min(), data["Year"].max()],
            y=[0, 0],
            mode="lines",
            name="Baseline",
            line=dict(color="gray", dash="dash")
        ))

        # Highlight Negative Net Worth Areas
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

        # -------------------------------
        # Define X-Axis Ticks for Year and Age
        # -------------------------------
        # Set ticks every 5 years on the Year axis
        year_min, year_max = int(data["Year"].min()), int(data["Year"].max())
        year_ticks = np.arange(year_min, year_max + 1, 5)

        # Map Year ticks to Age values using nearest available data
        age_ticks = np.interp(year_ticks, data["Year"], data["Age"]).astype(int)

        # Update layout with dual x-axes
        fig.update_layout(
                width=500,  
                height=500,  # Adjust height but ensure no data loss
                margin=dict(l=50, r=50, t=50, b=50),  # Add margins
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

        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        # -------------------------------
        # Create and Offer Download of Excel File
        # -------------------------------
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