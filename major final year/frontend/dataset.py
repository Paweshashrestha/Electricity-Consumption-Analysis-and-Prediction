import os
import streamlit as st
import pandas as pd
import subprocess
import sys
def remove_zeros_and_format_date(date_value):
    if isinstance(date_value, str):
        date_value = pd.to_datetime(date_value, errors='coerce')

    if pd.notna(date_value) and date_value.hour == 0 and date_value.minute == 0 and date_value.second == 0:
        return date_value.strftime('%Y-%m-%d')
    return pd.NaT
def filter_by_year_month(df, year, month):
    start_date = pd.to_datetime(f"{year}-{month}-01", format='%Y-%m-%d')
    end_date = start_date + pd.offsets.MonthEnd(0)
    return df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()
def dataset():
    st.write("Welcome to dataset!")

    st.title(":bar_chart: Electricity")

    fl = st.file_uploader(":file_folder: Upload a file", type=([ "xlsx"]))

    if fl is not None:
        filename = fl.name
        st.write(filename)
        df = pd.read_excel(fl)

        # Save the uploaded file to the specified location
        save_path = "./dataset/input/final dataset.xlsx"
        df.to_excel(save_path, index=False)
        st.success(f"File saved successfully ")

        st.dataframe(df)

        # Run the cleaning script
        python_executable = sys.executable
        cleaning_script_path = "./backend/cleaning_overall.py"
        
        # Verify if the cleaning script exists
        if not os.path.exists(cleaning_script_path):
            st.error(f"Error: Cleaning script '{cleaning_script_path}' not found.")
        else:
            st.info(f"Running cleaning script")
            result = subprocess.run([python_executable, cleaning_script_path], capture_output=True, text=True)
            st.write(result.stdout)
            st.error(result.stderr)

    else:
        default_files = [
            "./dataset/input/refined_data_all.xlsx",
            "./dataset/input/dataset.xlsx"
        ]
        for file in default_files:
            if file == "./dataset/input/dataset.xlsx":
               
                df = pd.read_excel(file)
               
                date_column = 'Date'
                df[date_column] = df[date_column].apply(remove_zeros_and_format_date)
 
                df = df.dropna(subset=[date_column])
 
                st.dataframe(df)
                      

                # Date filter for the specified file
                col1, col2 = st.columns(2)
                if "Date" in df.columns:
                    startDate = pd.to_datetime(df["Date"]).min()
                    endDate = pd.to_datetime(df["Date"]).max()
                    date1 = pd.to_datetime(col1.date_input("Start Date", startDate))
                    date2 = pd.to_datetime(col2.date_input("End Date", endDate))

                    filtered_df = df[(pd.to_datetime(df["Date"]) >= date1) & (pd.to_datetime(df["Date"]) <= date2)].copy()

                    st.dataframe(filtered_df)
                else:
                    st.warning("The default file does not contain a 'Date' column.")
            else:
                df = pd.read_excel(file)
                st.dataframe(df)


# Call the dataset function when needed
if hasattr(st.session_state, 'show_dataset') and st.session_state.show_dataset:
    dataset()
