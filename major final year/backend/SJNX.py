from flask import Flask, jsonify, request
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import time

start_time = time.time()

app = Flask(__name__)

# Load preprocessed data
excel_file_path = "./dataset/input/refined_data_all.xlsx"

df = pd.read_excel(excel_file_path)

# Define features and target variable
features = ['YEAR', 'MONTH', 'DAY', 'HOUR', 'DAY_OF_THE_WEEK', 'IS_HOLIDAY', 'TEMPERATURE']
X = df[features]
y = df['ELECTRICITY']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

def vaue():
    pass

def train_xgboost(X_train, y_train):
    return XGBRegressor().fit(X_train, y_train)


def predict(model, X_test):
    return model.predict(X_test)


# Train linear regression, KNN, XGBoost models
models = {}
models['xgboost'] = train_xgboost(X_train, y_train)


def validate_input(data):
    required_keys = ['bs_year', 'bs_month', 'bs_day', 'day_of_week_number', 'is_holiday', 'selected_model', 'temperatures']

    for key in required_keys:
        if key not in data:
            return False, f'Missing required key: {key}'

    for key in ['bs_year', 'bs_month', 'bs_day', 'day_of_week_number']:
        if not isinstance(data[key], int):
            return False, f'{key} should be an integer'

    if 'is_holiday' in data:
        if not isinstance(data['is_holiday'], int):
            return False, 'is_holiday should be an integer (0 or 1)'

    if 'temperatures' in data:
        if not isinstance(data['temperatures'], list):
            return False, 'temperatures should be a list'
    
    return True, None


@app.route('/predict_demand', methods=['POST'])
def predict_demand():
    try:
        data = request.json  # Get the JSON data from the request

        # Validate the input data format
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        data = request.json  # Get the JSON data from the request
        app.logger.info(f"Received data: {data}")


        # Extract data
        day_of_week_number = data['day_of_week_number']
        is_holiday = data['is_holiday']
        bs_year = data['bs_year']
        bs_month = data['bs_month']
        bs_day = data['bs_day']
        ad_date = data['ad_date']
        selected_model = data['selected_model']
        temperatures = data['temperatures']
        prediction_hours = list(range(1, 25))

        print(f"BS Date: {bs_year}/{bs_month}/{bs_day}, "
              f"Day of Week: {day_of_week_number}, "
              f"Is Holiday: {is_holiday}, "
              f"Selected Model: {selected_model}, "
              f"Temperatures: {temperatures}")

        # Example: Predict demand using the specified model
        model = models[selected_model]
        if len(temperatures) != 24:
            return jsonify({'error': 'Temperatures should be a list of 24 values'}), 400
        prediction_data = pd.DataFrame({
            'YEAR': [bs_year] * len(prediction_hours) ,
            'MONTH': [bs_month] * len(prediction_hours),
            'DAY': [bs_day] * len(prediction_hours),
            'HOUR': prediction_hours,
            'DAY_OF_THE_WEEK': [day_of_week_number]*len(prediction_hours),
            'IS_HOLIDAY': [is_holiday] * len(prediction_hours),
            'TEMPERATURE': temperatures
        })
      
        predicted_demand = predict(model, prediction_data)
        # Check if the selected model is XGBoost
        if selected_model == 'xgboost':
    # Convert NumPy arrays to lists for XGBoost predictions
         predicted_demand = predicted_demand.tolist()

        # Example: Respond with a success message and predicted demand
        response = {
            'message': f'Demand predictions received from the backend for BS Date: {bs_year}/{bs_month}/{bs_day}:',
            'predictions': [{'hour': h, 'demand': round(d, 2)} for h, d in zip(range(1, 25), predicted_demand)]
        }
        print(response)
        return jsonify(response), 200
        
    except Exception as e:
        # Handle any errors that might occur during processing
        response = {'error': str(e)}
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)


