import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime
 
 
def remove_zeros_and_format_date(date_value):
    if isinstance(date_value, str):
        date_value = pd.to_datetime(date_value, errors='coerce')
 
    if pd.notna(date_value) and not pd.isnat(date_value):
        # Extract only the month and year and format as mm/yyyy
        return date_value.strftime('%m/%Y')
    return pd.NaT
 
def filter_by_year_month(df, year, month):
    start_date = f"{year}-{month}-01"
    end_date = pd.to_datetime(start_date) + pd.offsets.MonthEnd(0)
    return df[(df["DATE"] >= start_date) & (df["DATE"] <= end_date)].copy()
 
 
def dashboard():
    st.header("Welcome to the electricity consumption analysis of Baneshwor!")
 
     # Add Google Maps iframe
    st.components.v1.iframe("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d14130.927001396656!2d85.33981835!3d27.6946846!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39eb199a06c2eaf9%3A0xc5670a9173e161de!2sNew%20Baneshwor%2C%20Kathmandu%2044600!5e0!3m2!1sen!2snp!4v1708759100172!5m2!1sen!2snp", width=600, height=450)
 
    # Load data from Excel file
    # Load data from Excel file
    filepath = "./dataset/input/refined_data_all.xlsx"
    df = pd.read_excel(filepath)
 
# Convert 'DATE' column to datetime format
    df['DATE'] = pd.to_datetime(df['DATE'])
 
# Sidebar widgets
    date_range = st.date_input("Select Date Range", [df['DATE'].min(), df['DATE'].max()])
 
 
    hour_range = st.slider("Select Hour Range", 1, 24, [1, 24])
    temperature_range = st.slider("Select Temperature Range", int(df['TEMPERATURE'].min()), int(df['TEMPERATURE'].max()), [int(df['TEMPERATURE'].min()), int(df['TEMPERATURE'].max())])
 
    # Convert date_range to datetime
    date_range = [datetime.combine(date_range[0], datetime.min.time()), datetime.combine(date_range[1], datetime.max.time())]
 
    # Filter data based on user input
    filtered_df = df[(pd.to_datetime(df['DATE']) >= date_range[0]) & (pd.to_datetime(df['DATE']) <= date_range[1]) &
                     (df['HOUR'].between(hour_range[0], hour_range[1])) &
                     (df['TEMPERATURE'].between(temperature_range[0], temperature_range[1]))]
 
    # Mapping of numeric representation of Nepali months to their names
    nepali_month_names = {
        1: 'Baisakh', 2: 'Jestha', 3: 'Ashad', 4: 'Shrawan', 5: 'Bhadra', 6: 'Ashwin',
        7: 'Kartik', 8: 'Mangsir', 9: 'Poush', 10: 'Magh', 11: 'Falgun', 12: 'Chaitra'
    }
 
    def map_month_to_season(month):
        if month in ['Baisakh', 'Chaitra']:
            return 'Spring'
        elif month in ['Jestha', 'Ashad']:
            return 'Summer'
        elif month in ['Shrawan', 'Bhadra']:
            return 'Rainy'
        elif month in ['Ashwin', 'Kartik']:
            return 'Autumn'
        elif month in ['Mangsir', 'Poush']:
            return 'Pre Winter'
        elif month in ['Magh', 'Falgun']:
            return 'Winter'
 
    def plot_electricity_consumption(df):
        try:
            # Filter data for the month of Kartik and the year 2080
            df_kartik_2080 = df[(df['MONTH'] == 'Kartik') & (df['YEAR'] == 2080)]
 
            if df_kartik_2080.empty:
                st.warning("No data available for Kartik.")
                return
 
            # Filter data for Tihar and Dashain
            tihar_data = df_kartik_2080[(df_kartik_2080['DAY'].between(25, 29))]
            dashain_data = df_kartik_2080[(df_kartik_2080['DAY'].between(4, 9))]
 
            # Convert "DATE" column to date (remove time part)
            tihar_data['DATE'] = pd.to_datetime(tihar_data['DATE'])
            dashain_data['DATE'] = pd.to_datetime(dashain_data['DATE'])
 
            # Group by hour of the day (HR) for each dataset
            tihar_hourly_average = tihar_data.groupby('HOUR')['ELECTRICITY'].mean()
            dashain_hourly_average = dashain_data.groupby('HOUR')['ELECTRICITY'].mean()
 
            # Create traces for Tihar and Dashain
            data = [
                go.Scatter(x=tihar_hourly_average.index, y=tihar_hourly_average.values, mode='lines', name='Tihar'),
                go.Scatter(x=dashain_hourly_average.index, y=dashain_hourly_average.values, mode='lines', name='Dashain')
            ]
 
            # Define layout
            layout = go.Layout(title='Average Electricity Consumption for Kartik in Megawatt',
                               xaxis=dict(title='Hour of the Day'),
                               yaxis=dict(title='Average Electricity Consumption in MW'))
 
            # Create figure
            fig = go.Figure(data=data, layout=layout)
 
            # Display the plot
            st.plotly_chart(fig)
 
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
 
    def plot_daily_hourly_average(filtered_df):
        day_mapping = {'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4, 'Thursday': 5, 'Friday': 6, 'Saturday': 7}
        filtered_df['DAY_OF_THE_WEEK'] = filtered_df['DAY_OF_THE_WEEK'].map(day_mapping)
 
        # Convert "DATE" column to date (remove time part)
        filtered_df['DATE'] = filtered_df['DATE'].dt.date
 
        # Group by day of the week (DOTW) and hour of the day (HR), then calculate the average electricity consumption for each hour
        grouped = filtered_df.groupby(['DAY_OF_THE_WEEK', 'HOUR'])
        daily_hourly_average = grouped['ELECTRICITY'].mean().unstack()
        
 
        # Create traces for each day of the week
        data = []
        for DOTW in range(1, 8):
            if DOTW in daily_hourly_average.index:  # Check if the day of the week exists in the data
                trace = go.Scatter(x=daily_hourly_average.columns, y=daily_hourly_average.loc[DOTW].values, mode='lines', name=f'{list(day_mapping.keys())[list(day_mapping.values()).index(DOTW)]}')
 
                data.append(trace)
 
        # Define layout
        layout = go.Layout(title='Average Electricity Consumption vs Hour of the Day by Day of the Week in Megawatt',
                           xaxis=dict(title='Hour of the Day'),
                           yaxis=dict(title='Average Electricity Consumption in MW'),
                           legend=dict(title='Day of the Week'))
 
        # Create figure
        fig = go.Figure(data=data, layout=layout)
 
        # Display the plot
        st.plotly_chart(fig)
 
    def plot_monthly_hourly_average(df):
    # Assuming 'MONTH' column contains numeric representation of Nepali months, and you're mapping them to their names
        df['MONTH'] = df['MONTH'].map(nepali_month_names)
 
    # Group by month (MONTH) and hour of the day (HOUR), then calculate the average electricity consumption for each hour
        grouped = df.groupby(['MONTH', 'HOUR'])
        monthly_hourly_average = grouped['ELECTRICITY'].mean().unstack()
 
    # Create traces for each month
        data = []
        for month in df['MONTH'].unique():
            trace = go.Scatter(x=monthly_hourly_average.columns, y=monthly_hourly_average.loc[month].values, mode='lines', name=month)
            data.append(trace)
 
    # Define layout
        layout = go.Layout(title='Average Electricity Consumption vs Hour of the Day by Nepali Month in Megawatt',
                       xaxis=dict(title='Hour of the Day'),
                       yaxis=dict(title='Average Electricity Consumption in MW'),
                       legend=dict(title='Month'))
 
    # Create figure
        fig = go.Figure(data=data, layout=layout)
 
    # Display the plot using Streamlit
        st.plotly_chart(fig)
 
 
    def description(df):
    # Convert 'DATE' column to datetime format
        df['DATE'] = pd.to_datetime(df['DATE'])
 
    # Major KPI
        total_consumption = df['ELECTRICITY'].sum()
        average_consumption = df['ELECTRICITY'].mean()
        max_consumption = df['ELECTRICITY'].max()
        min_consumption = df['ELECTRICITY'].min()
 
    # Display Major KPIs
        st.subheader("Major Key Performance indicators (KPIs)")
        st.info(f"Total Consumption: {total_consumption:.2f} megawatt")
        st.info(f"Average Consumption: {average_consumption:.2f} megawatt")
        st.info(f"Maximum Consumption: {max_consumption:.2f} megawatt")
        st.info(f"Minimum Consumption: {min_consumption:.2f} megawatt")
 
    # Consumption Chart
        st.subheader("Electricity Consumption Over Time in Megawatt")
        fig_consumption = px.line(df, x=df['DATE'].dt.strftime('%Y-%m-%d'), y='ELECTRICITY', title='Electricity Consumption Over Time in Megawatt')
 
        fig_consumption.update_xaxes(type='category', title='Date')
        st.plotly_chart(fig_consumption)
 
 
        # Consumption Chart - Average Electricity Consumption per Month
        st.subheader("Average Electricity Consumption per Month in Megawatt")
 
        # Group by MonthYear and calculate the average electricity consumption
        grouped_data_monthly = df.groupby(['DATE'])['ELECTRICITY'].mean().reset_index()
 
        # Convert 'DATE' column to pandas datetime format
        grouped_data_monthly['DATE'] = pd.to_datetime(grouped_data_monthly['DATE'], format='%m/%Y')
 
        # Create line chart
        fig_avg_consumption = px.line(grouped_data_monthly,
                              x=grouped_data_monthly['DATE'].dt.strftime('%Y-%m-%d'),
                              y='ELECTRICITY',  
                              labels={'x': 'DATE', 'ELECTRICITY': 'Average Electricity Consumption in MW'},
                              title='Average Electricity Consumption per Month in Megawatt')
 
 
        fig_avg_consumption.update_xaxes(type='category')  # Set x-axis type to category to display date in yyyy-mm-dd format
        st.plotly_chart(fig_avg_consumption)
 
        # Day of Week Pie Chart - Average Electricity Consumption
        st.subheader("Average Electricity Consumption by Day of the Week in Megawatt")
        # Map day numbers to names
        day_mapping = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
        df['DAY_OF_THE_WEEK'] = df['DAY_OF_THE_WEEK'].map(day_mapping)
        fig_day_of_week = px.pie(df.groupby('DAY_OF_THE_WEEK')['ELECTRICITY'].mean().reset_index(),
                                  names='DAY_OF_THE_WEEK', values='ELECTRICITY',
                                  title='Average Electricity Consumption by Day of the Week in Megawatt')
        st.plotly_chart(fig_day_of_week)
 
    def plot_season_monthly_consumption(df):
        # Define layout for Plotly season plot
        season_layout = go.Layout(title='Average Electricity Consumption vs Hour of the Day by Season in Megawatt',
                                  xaxis=dict(title='Hour of the Day'),
                                  yaxis=dict(title='Average Electricity Consumption in MW'),
                                  legend=dict(title='Season'))
 
        # Replace numeric representation of Nepali months with their names
        df['MONTH'] = df['MONTH'].map(nepali_month_names)
 
        # Group by season and hour of the day (HR), then calculate the average electricity consumption for each hour
        grouped = df.groupby(['seasons', 'HOUR'])
        seasonal_hourly_average = grouped['ELECTRICITY'].mean().unstack()
 
        # Create traces for each season
        season_data = []
        for seasons in ['Spring', 'Monsoon', 'Autumn', 'Winter', 'Rainy', 'Pre Winter', 'Summer']:
            if seasons in seasonal_hourly_average.index:  # Check if the season exists in the data
                trace = go.Scatter(x=seasonal_hourly_average.loc[seasons].index,
                                   y=seasonal_hourly_average.loc[seasons].values, mode='lines', name=seasons)
                season_data.append(trace)
 
        # Create Plotly season figure
        season_fig = go.Figure(data=season_data, layout=season_layout)
        st.plotly_chart(season_fig)
 
        
 
    description(filtered_df)
    plot_daily_hourly_average(filtered_df)
    plot_monthly_hourly_average(filtered_df)
    plot_electricity_consumption(filtered_df)
    plot_season_monthly_consumption(filtered_df)
 
if __name__ == "__main__":
    dashboard()
 