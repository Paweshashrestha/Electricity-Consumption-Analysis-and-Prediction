import pandas as pd
import streamlit as st
import nepali_datetime
from datetime import datetime, timedelta
import requests
from nepali_datetime import date as nepali_date
import plotly.express as px

def convert_to_ad_date(bs_year, bs_month, bs_day):
    bs_date = nepali_datetime.date(bs_year, bs_month, bs_day)
    ad_date = bs_date.to_datetime_date()
    return ad_date

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

def calculate_kpis(predictions_data):
    # Calculate KPIs from predictions_data DataFrame
    total_demand = predictions_data['demand'].sum()
    average_demand = predictions_data['demand'].mean()
    max_demand = predictions_data['demand'].max()
    min_demand = predictions_data['demand'].min()
    
    # Find peak hour
    peak_hour = predictions_data.loc[predictions_data['demand'] == max_demand, 'hour'].iloc[0]

    return total_demand, average_demand, max_demand, min_demand, peak_hour

def display_kpis(total_demand, average_demand, max_demand, min_demand, peak_hour):
    st.subheader("Key Performance Indicators (KPIs)")
    st.info(f"Total Demand: {total_demand:.2f} megawatt")
    st.info(f"Average Demand: {average_demand:.2f} megawatt")
    st.info(f"Maximum Demand: {max_demand:.2f} megawatt")
    st.info(f"Minimum Demand: {min_demand:.2f} megawatt")
    st.info(f"Peak Hour: {peak_hour:.2f}")

def is_selected_date_holiday(holidays, selected_date):
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    for holiday in holidays:
        if holiday.get('date') == selected_date_str:
            return True, holiday.get('name')
    return False, None

def get_day_of_week_number(day_of_week):
    # Map day of the week to a number (1 to 7)
    day_number_mapping = {
        'Monday': 2,
        'Tuesday': 3,
        'Wednesday': 4,
        'Thursday': 5,
        'Friday': 6,
        'Saturday': 7,
        'Sunday': 1,
    }
    return day_number_mapping.get(day_of_week, 0)

def prediction():
    st.write("Welcome to prediction!")

    # Take input for Nepali month, day, and year
    bs_year = st.number_input("Enter Nepali Year", min_value=1970, max_value=2100, value=2078)
    bs_month = st.selectbox("Select Month", range(1, 13))
    bs_day = st.number_input("Select Day", min_value=1, max_value=32, value=1)

    submit_button = st.button("Submit")

    if submit_button:
        ad_date = convert_to_ad_date(bs_year, bs_month, bs_day)
        day_of_week = ad_date.strftime("%A")
        holidays = get_holidays(ad_date.year)
        day_of_week_number = get_day_of_week_number(day_of_week)

        is_holiday_today, holiday_name_today = is_selected_date_holiday(holidays, ad_date)

        if is_holiday_today:
            display_predictions(ad_date, bs_year, bs_month, bs_day, 1)
        else:
            display_predictions(ad_date, bs_year, bs_month, bs_day, 0)

def display_predictions(ad_date, bs_year, bs_month, bs_day, is_holiday):
    api_endpoint = "http://127.0.0.1:5002/"
    selected_model = "xgboost"
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
    else:
        st.write(f"Failed to get temperature predictions. API responded with status code: {response.status_code}")

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
            df_predictions['hour'] = pd.to_numeric(df_predictions['hour'])

            # Convert hour to floating-point format with increments of 1.00
            df_predictions['hour'] = df_predictions['hour'] + 1.00
            
            total_demand, average_demand, max_demand, min_demand, peak_hour = calculate_kpis(df_predictions)
            display_kpis(total_demand, average_demand, max_demand, min_demand, peak_hour)

            fig_line = px.line(df_predictions, x='hour', y='demand', title='Demand Predictions(Line Chart)',
                   labels={'hour': 'Hour', 'demand': 'Electricity Demand in Megawatt'})
            st.plotly_chart(fig_line)

            fig_bar = px.bar(df_predictions, x='hour', y='demand', title='Demand Predictions (Bar Chart)',
                 labels={'hour': 'Hour', 'demand': 'Electricity Demand in Megawatt'},
                 color='demand', color_discrete_map={0: '#964B00', 1: '#A0522D', 2: '#CD853F'})
            st.plotly_chart(fig_bar)
        else:
            st.write(f"Failed to send data. API responded with status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error sending data to the backend: {str(e)}")

if __name__ == "__main__":
    prediction()

