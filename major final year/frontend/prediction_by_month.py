import time
import pandas as pd
import streamlit as st
import nepali_datetime
from datetime import datetime, timedelta
import requests
from nepali_datetime import date as nepali_date
import plotly.express as px
import os
import calendar


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

        current_date = datetime(year, 1, 1)
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

def prediction_by_month():
    st.write("Welcome to prediction!")
    
    selected_model = "xgboost"
    year = st.number_input("Enter Year:", min_value=2080, max_value=2100)
    month = st.number_input("Enter Month:", min_value=1, max_value=12)
 
    if st.button("Submit"):
        try:
            start_time = time.time()  # Record the start time
            
            combined_data = pd.read_csv("./combined_predictions.csv")
 
            csv_filename = "combined_predictions.csv"
            if os.path.exists(csv_filename):
                os.remove(csv_filename)

            # Calculate start and end date for the selected month
            start_date_bs = f"{year}-{month:02d}-01"
            end_date_bs = f"{year}-{month:02d}-" + str(calendar.monthrange(year, month)[1])
            
            # Filter data based on selected date range
            mask = (pd.to_datetime(combined_data['date']) >= start_date_bs) & \
                   (pd.to_datetime(combined_data['date']) <= end_date_bs)
            filtered_data = combined_data.loc[mask]


 
            for current_date in pd.date_range(start=start_date_bs, end=end_date_bs):
                bs_year, bs_month, bs_day = current_date.year, current_date.month, current_date.day
                day_of_week = current_date.strftime("%A")
                holidays = get_holidays(current_date.year)
                is_holiday_today, _ = is_selected_date_holiday(holidays, current_date)
                day_of_week_number = get_day_of_week_number(day_of_week)
                display_predictions(current_date, bs_year, bs_month, bs_day, is_holiday_today, selected_model)
            file_path = "combined_predictions.csv"

            demand_data = read_demand_from_csv(file_path)

            total_demand, average_demand, max_demand, min_demand = calculate_kpis(demand_data)

            display_kpis(total_demand, average_demand, max_demand, min_demand)    
            display_aggregated_graph_line()
            display_aggregated_graph_bar()

 
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
    try:
        csv_filename = "combined_predictions.csv"
        combined_data = pd.read_csv(csv_filename)
        aggregated_data_line = combined_data.groupby('date')['demand'].mean().reset_index()
        
        # Check if the range of dates is more than 2 years
        date_range = pd.to_datetime(aggregated_data_line['date'])
        
            # Format tick labels to display only months
        tickformat = '%d-%m-%Y'
        
        # Plotting with more attractive line color
        fig_demand_aggregated_line = px.line(aggregated_data_line, x='date', y='demand', title='Aggregated Electricity Demand in MegaWatt vs Date', 
                                              color_discrete_sequence=['#bcbd22'])  
        
        # Update y-axis label
        fig_demand_aggregated_line.update_yaxes(title='Electricity Demand in MegaWatt')
        
        # Update x-axis tick format
        fig_demand_aggregated_line.update_xaxes(tickformat=tickformat)
        
        st.plotly_chart(fig_demand_aggregated_line)
    except Exception as e:
        st.error(f"Error displaying aggregated graph: {str(e)}")

def get_holidays_from_excel():
    try:
        excel_path = 'holidays.xlsx'
        holidays_df = pd.read_excel(excel_path)
        return holidays_df['date'].dt.strftime('%Y-%m-%d').tolist()  # Convert dates to string format
    except Exception as e:
        print(f"Error reading holidays from Excel: {str(e)}")
        return []
    
def display_aggregated_graph_bar():
    try:
        # Load combined predictions data
        csv_filename = "combined_predictions.csv"
        combined_data = pd.read_csv(csv_filename)
        aggregated_data = combined_data.groupby('date')['demand'].mean().reset_index()

        # Fetch holidays from Excel
        holidays_list = get_holidays_from_excel()
        
        # Mark holidays from Excel in the aggregated data
        aggregated_data['is_holiday'] = aggregated_data['date'].isin(holidays_list)
        
        # Mark Saturdays as holidays in the aggregated data
        aggregated_data['is_saturday'] = pd.to_datetime(aggregated_data['date']).dt.dayofweek == 6
        
        # Combine holiday and Saturday flags
        aggregated_data['is_holiday'] = aggregated_data['is_holiday'] | aggregated_data['is_saturday']
        
        # Plotting with more attractive colors
        fig_demand_bar = px.bar(aggregated_data, x='date', y='demand', title='Aggregated Electricity Demand in MegaWatt vs Date', 
                                 color='is_holiday', color_discrete_map={False: '#DAA06D', True: '#6E260E'})
        
        # Update y-axis label
        fig_demand_bar.update_yaxes(title='Electricity Demand in MegaWatt')
        
        # Customize plot layout for better appearance
        fig_demand_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='black'
        )

        # Display dates in 'yyyy-mm-dd' format
        fig_demand_bar.update_xaxes(tickformat="%Y-%m-%d")

        st.plotly_chart(fig_demand_bar)
    except Exception as e:
        st.error(f"Error displaying aggregated bar graph: {str(e)}")

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
            csv_filename = "combined_predictions.csv"
            if os.path.exists(csv_filename):
                existing_data = pd.read_csv(csv_filename)
                combined_data = pd.concat([existing_data, df_predictions], ignore_index=True)
            else:
                combined_data = df_predictions.copy()
            combined_data.to_csv(csv_filename, index=False)
        else:
            st.write(f"Failed to send data. API responded with status code: {response.status_code}")
    except Exception as e:
        # st.error(f"Error sending data to the backend: {str(e)}")
        print("Error sending data to the backend:" ,e)
 
if __name__ == "__main__":
    prediction_by_month()
