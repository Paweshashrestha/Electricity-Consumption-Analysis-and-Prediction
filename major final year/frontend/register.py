# streamlit_app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import subprocess
 
def register(fullname, email, password, repeat_password):
    # Make a request to the PHP backend for registration
    php_url = "http://localhost/hdeuie/registration.php"
    response = requests.post(
        php_url,
        data={
            "fullname": fullname,
            "email": email,
            "password": password,
            "repeat_password": repeat_password,
            "submit": "Register",  # Add the submit field
        },
    )
 
    # Extract the error message from the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    error_message = soup.find('div', class_='alert-danger').text if soup.find('div', class_='alert-danger') else None
 
    # Display the error message or success message
    if error_message:
        st.error(f"Registration failed. Server response: {error_message}")
    elif "success" in response.text:
        st.success("Registration successful!")
        # Redirect or show further content as needed
 
def main():
    st.title("Electricity Consumption Analysis and Prediction")
 
    # Streamlit UI for registration
    fullname = st.text_input("Full Name:")
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    repeat_password = st.text_input("Repeat Password:", type="password")
    if st.button("Register"):
        register(fullname, email, password, repeat_password)
 
    # Link to the login page
    if st.button("Login Here"):
        subprocess.run(["streamlit", "run", "./frontend/main.py"])
 
if __name__ == "__main__":
    main()
 