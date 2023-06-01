import subprocess
import streamlit as st
from streamlit_option_menu import option_menu
from login import login, register
from dashboard import dashboard
from dataset import dataset
from prediction import prediction
from about import about
from prediction_by_month import prediction_by_month
from prediction_by_year import prediction_by_year

user_emoji='⚡'

# st.set_page_config(page_title='Electricity Demand Forecast With Machine Learning', page_icon='⚡')
 
def main():
    st.title("Electricity Consumption Analysis and Prediction")
 
    # Initialize session variable for login status and user email
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = ""
 
    # Streamlit UI for login or registration
    if not st.session_state.logged_in:
        email_login = st.text_input("Email :")
        password_login = st.text_input("Password :", type="password")
        login_button = st.button("Login")
 
        if st.button("Not registered yet? Register Here"):
            subprocess.run(["streamlit", "run", "./frontend/register.py"])
 
        if login_button:
            login_successful = login(email_login, password_login)
            if login_successful:
                st.session_state.logged_in = True
                st.session_state.user_email = email_login
 
    else:
        # Sidebar navigation for the dashboard
        with st.sidebar:        
            # Use st.markdown to display the emoji
            st.markdown(f"# {user_emoji} Electricity Consumption Analysis and Prediction")
 
            app = option_menu(
                menu_title='',
                options=['Dashboard','Dataset','Prediction by day','Prediction by month','Prediction by year','about', 'Logout'],
                icons=['bar-chart','folder','clock','clock','clock','info-circle-fill', 'box-arrow-right'],
                default_index=1,
                styles={
                    "container":{"padding": "5!important","background-color":'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
 
        if app == "Dashboard":
            dashboard()
        elif app == "Dataset":
            dataset()
        elif app == "Prediction by day":
            prediction()
        elif app == "Prediction by month":
            prediction_by_month()
        elif app == "Prediction by year":
            prediction_by_year()
        elif app == "about":
            about()
 
        elif app == "Logout":
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.experimental_rerun()  # Rerun the app to show the login screen
 
if __name__ == "__main__":
    main()