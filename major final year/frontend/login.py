# login_and_register.py
import streamlit as st
import requests
from bs4 import BeautifulSoup

def login(email, password):
    # Make a request to the PHP backend for login
    php_url = "http://localhost/hdeuie/login.php"
    data = {"email": email, "password": password, "login": "true"}  # Add a specific parameter for login
    response = requests.post(php_url, data=data)

    # Check the response and handle login logic
    if response.text == "success":
        st.success("Login successful!")
        # Set a session variable to indicate successful login
        st.session_state.logged_in = True
    elif "Password does not match" in response.text:
        st.error("Password does not match. Check your credentials.")
    elif "Email does not match" in response.text:
        st.error("Email does not match. Check your credentials.")
    else:
        st.error("An error occurred. Please try again.")
        st.error(f"Server response: {response.text}")

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
        # Set a session variable to indicate successful registration
        st.session_state.logged_in = True
