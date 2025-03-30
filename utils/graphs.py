import streamlit as st
import pandas as pd
import json
from streamlit.components.v1 import html

# # df = pd.read_excel("assets/other/dummy_data.xlsx")
# df["Date"] = pd.to_datetime(df["Date"])
# df['Year'] = df['Date'].dt.year.astype(int)  # Convert to integer type
# df['Month'] = df['Date'].dt.strftime('%m-%Y')
# df['Category'] = df['Category'].fillna('Untagged').astype(str)

def render_chart(chart_id, options):
    html_code = f"""
    <div id="{chart_id}" style="width: 100%; height: 400px; display: inline-block;"></div>
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/drilldown.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>

    <script>
    Highcharts.chart('{chart_id}', {json.dumps(options)});
    </script>
    """
    html(html_code, height=600)

def top_left(df):
    year_wise_credit = df.groupby('Year')['Credit'].sum().reset_index()
    year_wise_credit['Year'] = year_wise_credit['Year'].astype(str)

    # Creating Highcharts options
    credit_chart_options = {
        'chart': {'type': 'column'},
        'title': {'text': 'Year Wise Credit'},
        'xAxis': {'type': 'category'},
        'yAxis': {'title': {'text': 'Credit Amount'}},
        'series': [{
            'name': 'Credit',
            'colorByPoint': True,
            'data': [
                {
                    'name': row['Year'],
                    'y': float(row['Credit']),
                    'drilldown': row['Year']
                } for index, row in year_wise_credit.iterrows()
            ]
        }],
        'drilldown': {
            'series': []
        },
        'exporting': {
            'buttons': {
                'contextButton': {
                    'menuItems': [
                        "viewFullscreen"
                    ]
                }
            }
        },
        'credits': {
            'enabled': False
        }
    }

    for year in year_wise_credit['Year'].unique():
        category_data = df[df['Year'] == int(year)].groupby('Category')['Credit'].sum().reset_index()
        drilldown_series = {
            'id': year,
            'name': f'Category Wise Credit for {year}',
            'data': [
                {
                    'name': row['Category'],
                    'y': float(row['Credit']),
                    'drilldown': f'{year}-{row["Category"]}'
                } for index, row in category_data.iterrows()
            ]
        }
        credit_chart_options['drilldown']['series'].append(drilldown_series)

        for _, row in category_data.iterrows():
            category_name = row['Category']
            month_data = df[(df['Year'] == int(year)) & (df['Category'] == category_name)].groupby('Month')['Credit'].sum().reset_index()
            
            drilldown_series = {
                'id': f'{year}-{category_name}',
                'name': f'Month Wise Credit for {category_name} ({year})',
                'data': [
                    [row['Month'], float(row['Credit'])] for index, row in month_data.iterrows()
                ]
            }
            credit_chart_options['drilldown']['series'].append(drilldown_series)

    render_chart('top_left_graph', credit_chart_options)

def top_right(df):
    year_wise_debit = df.groupby('Year')['Debit'].sum().reset_index()
    year_wise_debit['Year'] = year_wise_debit['Year'].astype(str)

    # Creating Highcharts options
    debit_chart_options = {
        'chart': {'type': 'column'},
        'title': {'text': 'Year Wise debit'},
        'xAxis': {'type': 'category'},
        'yAxis': {'title': {'text': 'debit Amount'}},
        'series': [{
            'name': 'Debit',
            'colorByPoint': True,
            'data': [
                {
                    'name': row['Year'],
                    'y': float(row['Debit']),
                    'drilldown': row['Year']
                } for index, row in year_wise_debit.iterrows()
            ]
        }],
        'drilldown': {
            'series': []
        },
        'exporting': {
            'buttons': {
                'contextButton': {
                    'menuItems': [
                        "viewFullscreen"
                    ]
                }
            }
        },
        'credits': {
            'enabled': False
        }
    }

    for year in year_wise_debit['Year'].unique():
        category_data = df[df['Year'] == int(year)].groupby('Category')['Debit'].sum().reset_index()
        drilldown_series = {
            'id': year,
            'name': f'Category Wise debit for {year}',
            'data': [
                {
                    'name': row['Category'],
                    'y': float(row['Debit']),
                    'drilldown': f'{year}-{row["Category"]}'
                } for index, row in category_data.iterrows()
            ]
        }
        debit_chart_options['drilldown']['series'].append(drilldown_series)

        for _, row in category_data.iterrows():
            category_name = row['Category']
            month_data = df[(df['Year'] == int(year)) & (df['Category'] == category_name)].groupby('Month')['Debit'].sum().reset_index()
            
            drilldown_series = {
                'id': f'{year}-{category_name}',
                'name': f'Month Wise debit for {category_name} ({year})',
                'data': [
                    [row['Month'], float(row['Debit'])] for index, row in month_data.iterrows()
                ]
            }
            debit_chart_options['drilldown']['series'].append(drilldown_series)

    render_chart('top_left_graph', debit_chart_options)

def bottom_left(df):
    # Aggregating data for the initial Category-wise Credit graph
    category_wise_credit = df.groupby('Category')['Credit'].sum().reset_index()

    # Creating Highcharts options for Category-wise Credit graph
    credit_category_chart_options = {
        'chart': {'type': 'column'},
        'title': {'text': 'Category Wise Credit'},
        'xAxis': {'type': 'category'},
        'yAxis': {'title': {'text': 'Credit Amount'}},
        'series': [{
            'name': 'Credit',
            'colorByPoint': True,
            'data': [
                {
                    'name': row['Category'],
                    'y': int(row['Credit']),
                    'drilldown': row['Category']
                } for index, row in category_wise_credit.iterrows()
            ]
        }],
        'drilldown': {
            'series': []
        },
        'exporting': {
            'buttons': {
                'contextButton': {
                    'menuItems': [
                        "viewFullscreen"
                    ]
                }
            }
        },
        'credits': {'enabled': False}
    }

    # Adding Month-wise Credit drilldown data for each category
    for category in category_wise_credit['Category'].unique():
        month_data = df[df['Category'] == category].groupby('Month')['Credit'].sum().reset_index()
        
        drilldown_series = {
            'id': category,
            'name': f'Month Wise Credit for {category}',
            'data': [
                {
                    'name': row['Month'],
                    'y': int(row['Credit']),
                    'drilldown': f'{category}-{row["Month"]}'
                } for index, row in month_data.iterrows()
            ]
        }
        credit_category_chart_options['drilldown']['series'].append(drilldown_series)
        
        # Adding Date-wise Credit drilldown data for each month
        for _, row in month_data.iterrows():
            month_name = row['Month']
            date_data = df[(df['Category'] == category) & (df['Month'] == month_name)].groupby('Date')['Credit'].sum().reset_index()
            
            drilldown_series = {
                'id': f'{category}-{month_name}',
                'name': f'Date Wise Credit for {category} in {month_name}',
                'data': [
                    [str(row['Date'].date()), int(row['Credit'])] for index, row in date_data.iterrows()
                ]
            }
            credit_category_chart_options['drilldown']['series'].append(drilldown_series)

    # Render the Bottom Left graph
    render_chart('bottom_left_graph', credit_category_chart_options)

def bottom_right(df):
    # Aggregating data for the initial Category-wise Debit graph
    category_wise_debit = df.groupby('Category')['Debit'].sum().reset_index()

    # Creating Highcharts options for Category-wise Debit graph
    debit_category_chart_options = {
        'chart': {'type': 'column'},
        'title': {'text': 'Category Wise Debit'},
        'xAxis': {'type': 'category'},
        'yAxis': {'title': {'text': 'Debit Amount'}},
        'series': [{
            'name': 'Debit',
            'colorByPoint': True,
            'data': [
                {
                    'name': row['Category'],
                    'y': int(row['Debit']),
                    'drilldown': row['Category']
                } for index, row in category_wise_debit.iterrows()
            ]
        }],
        'drilldown': {
            'series': []
        },
        'exporting': {
            'buttons': {
                'contextButton': {
                    'menuItems': [
                        "viewFullscreen"
                    ]
                }
            }
        },
        'credits': {'enabled': False}
    }

    # Adding Month-wise Debit drilldown data for each category
    for category in category_wise_debit['Category'].unique():
        month_data = df[df['Category'] == category].groupby('Month')['Debit'].sum().reset_index()
        
        drilldown_series = {
            'id': category,
            'name': f'Month Wise Debit for {category}',
            'data': [
                {
                    'name': row['Month'],
                    'y': int(row['Debit']),
                    'drilldown': f'{category}-{row["Month"]}'
                } for index, row in month_data.iterrows()
            ]
        }
        debit_category_chart_options['drilldown']['series'].append(drilldown_series)
        
        # Adding Date-wise Debit drilldown data for each month
        for _, row in month_data.iterrows():
            month_name = row['Month']
            date_data = df[(df['Category'] == category) & (df['Month'] == month_name)].groupby('Date')['Debit'].sum().reset_index()
            
            drilldown_series = {
                'id': f'{category}-{month_name}',
                'name': f'Date Wise Debit for {category} in {month_name}',
                'data': [
                    [str(row['Date'].date()), int(row['Debit'])] for index, row in date_data.iterrows()
                ]
            }
            debit_category_chart_options['drilldown']['series'].append(drilldown_series)

    # Render the Bottom Right graph
    render_chart('bottom_right_graph', debit_category_chart_options)

# top_left(df)
# top_right(df)
# bottom_left(df)
# bottom_right(df)