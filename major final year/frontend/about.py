# dashboard_page_1.py
import streamlit as st
 
def about():
    st.title("About ")
 
    st.write(
        "In response to the escalating demand for electricity in our rapidly advancing world, the development of the Electricity Consumption Analysis and Prediction System becomes pivotal. With a focus on accurate forecasting for effective energy resource planning, the system integrates diverse algorithms such as KNN, linear regression, SVM, and XGBoost. Following thorough data cleaning, feature engineering, and integration processes, XGBoost stands out as the optimal model, ensuring superior accuracy in predicting electricity consumption. The system enhances user understanding through intuitive visualization of analyzed data and model predictions using charts and graphs. Furthermore, it provides predictions for electricity consumption on a monthly, daily, and yearly basis, contributing to efficient energy management."
    )
 
def main():
    # Add your main content here
    st.title("Electricity Demand Prediction Dashboard")
 
    # Create a sidebar with navigation links
    st.sidebar.title("Navigation")
    pages = ["Home", "About"]  # Add more pages if needed
    choice = st.sidebar.radio("Go to", pages)
 
    # Based on the user's choice, display the appropriate page
    if choice == "Home":
        st.header("Home Page")
        # Add content for the home page here
    elif choice == "About":
        about()  # Call the about function
