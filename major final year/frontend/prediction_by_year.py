import streamlit as st
import nepali_datetime
import requests
from nepali_datetime import date as nepali_date
import plotly.express as px
import os
import pandas as pd
from datetime import datetime, timedelta
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time
 
def convert_to_ad_date(date_str):
    try:
        bs_year, bs_month, bs_day = map(int, date_str.split('-'))
        bs_date = nepali_datetime.date(bs_year, bs_month, bs_day)
        ad_date = bs_date.to_datetime_date()
        return ad_date
    except ValueError:
        raise ValueError("Invalid date format. Please use 'YYYY-MM-DD' format.")
 
def read_demand_from_csv(file_path):
    demand = pd.read_csv(file_path)
    return demand
 
def calculate_kpis(demand_data):
    total_demand = demand_data['demand'].sum()
    average_demand = demand_data['demand'].mean()
    max_demand = demand_data['demand'].max()
    min_demand = demand_data['demand'].min()
    return total_demand, average_demand, max_demand, min_demand
 
def display_kpis(total_demand, average_demand, max_demand, min_demand):
    st.subheader("Key Performance Indicators (KPIs)")
    st.info(f"Total Demand: {total_demand:.2f} megawatt")
    st.info(f"Average Demand: {average_demand:.2f} megawatt")
    st.info(f"Maximum Demand: {max_demand:.2f} megawatt")
    st.info(f"Minimum Demand: {min_demand:.2f} megawatt")
    
 
def get_holidays(year):
    try:
        excel_path = 'holidays.xlsx'
        holidays_df = pd.read_excel(excel_path)
        holidays_for_year = holidays_df[holidays_df['bs_year'] == year]
        holidays_list = holidays_for_year.to_dict('records')
 
        current_date = nepali_date(year, 1, 1)
        while current_date.year == year:
            if current_date.weekday() == 6:  # Saturday
                holidays_list.append({
                    'name': 'Saturday',
                    'date': current_date.strftime('%Y-%m-%d'),
                })
            current_date += timedelta(days=1)
 
        return holidays_list
 
    except Exception as e:
        print(f"Error fetching holidays: {str(e)}")
        return []
 
 
 
 
def is_selected_date_holiday(holidays, selected_date):
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    for holiday in holidays:
        if holiday.get('date') == selected_date_str:
            return True, holiday.get('name')
    return False, None
 
def get_day_of_week_number(day_of_week):
    day_number_mapping = {
        'Monday': 2, 'Tuesday': 3, 'Wednesday': 4,
        'Thursday': 5, 'Friday': 6, 'Saturday': 7, 'Sunday': 1,
    }
    return day_number_mapping.get(day_of_week, 0)
 
def prediction_by_year():
    st.write("Welcome to prediction!")
    
    selected_model = "xgboost"
    year = st.number_input("Enter Year:", min_value=2080, max_value=2100)
 
    if st.button("Submit"):
        try:
            start_time = time.time()  # Record the start time
            
            # Load existing data or create an empty DataFrame if file doesn't exist
            csv_filename = "combined_year.csv"
            if os.path.exists(csv_filename):
                # Clear the content of the CSV file without removing the headers
                combined_data = pd.read_csv(csv_filename)
                combined_data = combined_data.iloc[0:0]  # Remove all rows
                combined_data.to_csv(csv_filename, index=False)  # Save empty DataFrame
            else:
                print("No existing data found in 'combined_year.csv'.")
 
            # Create an empty DataFrame
            combined_data = pd.DataFrame(columns=['date', 'demand'])
 
            # Calculate start and end date for the selected year
            start_date_bs = f"{year}-01-01"
            end_date_bs = f"{year}-12-31"
            
            # Filter data based on selected date range
            if not combined_data.empty:
                mask = (pd.to_datetime(combined_data['date']) >= start_date_bs) & \
                       (pd.to_datetime(combined_data['date']) <= end_date_bs)
                filtered_data = combined_data.loc[mask]
            else:
                filtered_data = pd.DataFrame()  # Create an empty DataFrame if combined_data is empty
 
            dates_info = []
            for current_date in pd.date_range(start=start_date_bs, end=end_date_bs):
                bs_year, bs_month, bs_day = current_date.year, current_date.month, current_date.day
                day_of_week = current_date.strftime("%A")
                holidays = get_holidays(current_date.year)
                is_holiday_today, _ = is_selected_date_holiday(holidays, current_date)
                day_of_week_number = get_day_of_week_number(day_of_week)
                predictions = display_predictions(current_date, bs_year, bs_month, bs_day, is_holiday_today, selected_model)
                dates_info.append((current_date, bs_year, bs_month, bs_day, is_holiday_today, selected_model))
                
 
            file_path = "combined_year.csv"
            demand_data = read_demand_from_csv(file_path)
 
            total_demand, average_demand, max_demand, min_demand = calculate_kpis(demand_data)
 
            display_kpis(total_demand, average_demand, max_demand, min_demand)
            display_aggregated_graph_line()
            display_aggregated_graph_bar()
            display_demand_pie_chart()
            end_time = time.time()  # Record the end time
            processing_time = end_time - start_time  # Calculate the elapsed time
            
            # Display the processing time
            # st.write(f"Processing time: {processing_time:.2f} seconds")
 
        except ValueError as e:
            st.error(str(e))
 
 
 
 
def display_predictions(ad_date, bs_year, bs_month, bs_day, is_holiday, selected_model):
    api_endpoint = "http://127.0.0.1:5002/"
    day_of_week_number = get_day_of_week_number(ad_date.strftime("%A"))
    data = {
        "day_of_week_number": day_of_week_number,
        "is_holiday": is_holiday,
        "ad_date": ad_date.strftime("%Y-%m-%d"),
        "bs_year": bs_year,
        "bs_month": bs_month,
        "bs_day": bs_day
    }
    response = requests.post(api_endpoint, json=data)
    if response.status_code == 200:
        predictions = response.json().get('predictions', [])
        send_to_backend(day_of_week_number, is_holiday, ad_date, bs_year, bs_month, bs_day, predictions, selected_model)
        return predictions
    return []
 

 
def display_aggregated_graph_line():
    csv_filename = "combined_year.csv"
    if os.path.exists(csv_filename):
        try:
            combined_data = pd.read_csv(csv_filename)
            aggregated_data_line = combined_data.groupby('date')['demand'].mean().reset_index()
 
            # Load holidays from holiday.xlsx
            holidays_df = pd.read_excel('holidays.xlsx')
            holidays_df['date'] = pd.to_datetime(holidays_df['date'])
            holidays_dict = holidays_df.set_index('date')['name'].to_dict()
 
            # Add holiday name to aggregated_data_line DataFrame
            aggregated_data_line['Holiday Name'] = aggregated_data_line['date'].map(holidays_dict)
            aggregated_data_line['Holiday Name'] = aggregated_data_line['Holiday Name'].fillna(0)  # Fill NaN with 0
 
            # Check if the range of dates is more than 2 years
            date_range = pd.to_datetime(aggregated_data_line['date'])
            if (date_range.max() - date_range.min()).days > 365 * 2:
                # Format tick labels to display only months
                tickformat = '%m\n%Y'
            else:
                # Format tick labels to display days when the range is within 2 years
                tickformat = '%d-%m-%Y'
 
            # Define hover data
            hover_data = {'date': '|%Y-%m-%d', 'demand': ':.2f', 'Holiday Name': True}
 
            fig_demand_aggregated_line = px.line(aggregated_data_line, x='date', y='demand',
                                                  title='Aggregated Electricity Demand in MegaWatt vs. Date',
                                                  labels={'date': 'Date', 'demand': 'Electricity Demand in MegaWatt'},  # Update labels
                                                  hover_data=hover_data,  # Include hover data
                                                  color_discrete_sequence=['#bcbd22']  # Change line color to green
                                                  )
            # Update x-axis tick format
            fig_demand_aggregated_line.update_xaxes(tickformat=tickformat)
 
            st.plotly_chart(fig_demand_aggregated_line)
        except Exception as e:
            st.error(f"Error displaying aggregated graph: {str(e)}")
    else:
        st.error("Data file 'combined_predictions.csv' not found. Creating a new file...")
        pd.DataFrame(columns=['date', 'demand']).to_csv(csv_filename, index=False)
        st.write(f"Empty file '{csv_filename}' created.")
 
 
# Main function for your Streamlit app
def main():
    st.title("Demand Analysis")
    
    # Display the aggregated demand graph
    st.subheader("Aggregated Electricity Demand")
    display_aggregated_graph_line()
 
if __name__ == "__main__":
    main()
 
 
 
 
 
 
 
# Define a dictionary to map month numbers to Nepali month names
month_names = {
    1: "Baisakh",
    2: "Jestha",
    3: "Asar",
    4: "Shrawan",
    5: "Bhadra",
    6: "Ashwin",
    7: "Kartik",
    8: "Mangsir",
    9: "Poush",
    10: "Magh",
    11: "Falgun",
    12: "Chaitra"
}
 
def display_aggregated_graph_bar():
    csv_filename = "combined_year.csv"
    if os.path.exists(csv_filename):
        try:
            combined_data = pd.read_csv(csv_filename)
            aggregated_data = combined_data.groupby('date')['demand'].mean().reset_index()
 
            # Simplify date format for every label if the difference between months is more than 2
            aggregated_data['date'] = pd.to_datetime(aggregated_data['date'])
            min_date = aggregated_data['date'].min()
            max_date = aggregated_data['date'].max()
            if (max_date - min_date).days / 30 > 2:
                # Extract month from the date and map it to month names
                aggregated_data['date'] = aggregated_data['date'].dt.month.map(month_names)
            else:
                # Extract month from the date and map it to month names
                aggregated_data['date'] = aggregated_data['date'].dt.month.map(month_names)
 
            # Define a color palette
            colors = px.colors.qualitative.Set3[:len(aggregated_data)]
            
            # Plot the bar graph with different colors
            fig_demand_bar = px.bar(aggregated_data, x='date', y='demand', title='Aggregated Electricity Demand in MegaWatt vs. Date',
                                     color='date', color_discrete_sequence=colors,
                                     labels={'date': 'Date', 'demand': 'Electricity Demand in MegaWatt'})  # Update labels
            fig_demand_bar.update_xaxes(type='category', tickmode='linear', dtick=1)
            fig_demand_bar.update_yaxes(title_text='Electricity Demand in MegaWatt')  # Update y-axis label
 
            st.plotly_chart(fig_demand_bar)
        except Exception as e:
            st.error(f"Error displaying aggregated bar graph: {str(e)}")
    else:
        st.error("Data file 'combined_year.csv' not found. Creating a new file...")
        pd.DataFrame(columns=['date', 'demand']).to_csv(csv_filename, index=False)
        st.write(f"Empty file '{csv_filename}' created.")
 
 
# Define a dictionary to map month numbers to Nepali month names
nepali_month_names = {
    1: "Baisakh",
    2: "Jestha",
    3: "Asar",
    4: "Shrawan",
    5: "Bhadra",
    6: "Ashwin",
    7: "Kartik",
    8: "Mangsir",
    9: "Poush",
    10: "Magh",
    11: "Falgun",
    12: "Chaitra"
}
 
def display_demand_pie_chart():
    csv_filename = "combined_year.csv"
    if os.path.exists(csv_filename):
        try:
            combined_data = pd.read_csv(csv_filename)
            # Convert date column to datetime type
            combined_data['date'] = pd.to_datetime(combined_data['date'])
            # Extract month from the date and map it to Nepali month names
            combined_data['month'] = combined_data['date'].dt.month.map(nepali_month_names)
            # Group data by month and calculate total demand for each month
            demand_by_month = combined_data.groupby('month')['demand'].sum().reset_index()
 
            # Plot the pie chart
            fig_demand_pie = px.pie(demand_by_month, values='demand', names='month', title='Demand Distribution by Month')
 
            st.plotly_chart(fig_demand_pie)
        except Exception as e:
            st.error(f"Error displaying demand pie chart: {str(e)}")
    else:
        st.error("Data file 'combined_year.csv' not found.")
 
# Main function for your Streamlit app
def main():
    st.title("Demand Analysis")
    
    # Display the demand distribution pie chart
    st.subheader("Demand Distribution by Month")
    display_demand_pie_chart()
 
if __name__ == "__main__":
    main()
 
 
def send_to_backend(day_of_week_number, is_holiday, ad_date, bs_year, bs_month, bs_day, predictions, selected_model):
    api_endpoint = "http://127.0.0.1:5003/predict_demand"
    predicted_temperatures = [round(float(prediction['temperature']), 2) for prediction in predictions]
    data = {
        'day_of_week_number': day_of_week_number,
        'is_holiday': is_holiday,
        'bs_year': bs_year,
        'bs_month': bs_month,
        'bs_day': bs_day,
        'ad_date': ad_date.strftime("%Y-%m-%d"),
        'selected_model': selected_model,
        'temperatures': predicted_temperatures
    }
    try:
        response = requests.post(api_endpoint, json=data)
        if response.status_code == 200:
            response_data = response.json()
            predictions_data = response_data.get('predictions', [])
            df_predictions = pd.DataFrame(predictions_data)
            bs_date_format = [nepali_datetime.date(bs_year, bs_month, bs_day).strftime("%Y-%m-%d") for _ in range(len(df_predictions))]
            df_predictions['date'] = bs_date_format
            csv_filename = "combined_year.csv"
            if os.path.exists(csv_filename):
                existing_data = pd.read_csv(csv_filename)
                combined_data = pd.concat([existing_data, df_predictions], ignore_index=True)
            else:
                combined_data = df_predictions.copy()
            combined_data.to_csv(csv_filename, index=False)
        else:
            st.write(f"Failed to send data. API responded with status code: {response.status_code}")
    except Exception as e:
        print("Error sending data to the backend:" ,e)
 
if __name__ == "__main__":
    prediction_by_year()