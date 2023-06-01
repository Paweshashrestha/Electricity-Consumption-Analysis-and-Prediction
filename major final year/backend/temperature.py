from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Load your Excel file into a pandas DataFrame
file_path = './dataset/input/temperature_only.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')  # Specify the engine, use 'xlrd' if needed

df['datetime'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY', 'HOUR']], errors='coerce')
df['hour_of_day'] = df['datetime'].dt.hour

# Model Training
X = df[['YEAR', 'MONTH', 'DAY', 'HOUR']]  # Features
y = df['TEMPERATURE']  # Target variable

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

def validate_input(data):
    required_keys = ['day_of_week_number', 'is_holiday', 'bs_year', 'bs_month', 'bs_day']
    for key in required_keys:
        if key not in data:
            return False, f'Missing required key: {key}'
    for key in ['bs_year', 'bs_month', 'bs_day']:
        if not isinstance(data[key], int):
            return False, f'{key} should be an integer'
    return True, None

@app.route('/', methods=['POST'])
def predict_temperature():
    data = request.get_json()

    # Validate input
    is_valid, error_message = validate_input(data)
    if not is_valid:
        return jsonify({'error': f'Invalid input data. {error_message}'}), 400

    bs_year = data['bs_year']
    bs_month = data['bs_month']
    bs_day = data['bs_day']
    prediction_hours = list(range(1, 25))

    prediction_data = pd.DataFrame({'YEAR': [bs_year] * len(prediction_hours),
                                     'MONTH': [bs_month] * len(prediction_hours),
                                     'DAY': [bs_day] * len(prediction_hours),
                                     'HOUR': prediction_hours})

    # Make predictions for the specified date and hours
    # Make predictions for the specified date and hours
    predicted_temperatures = model.predict(prediction_data)


    response = {'message': f'Temperature predictions received from the backend for BS Date: {bs_year}/{bs_month}/{bs_day}:',
            'predictions': [{'hour': hour, 'temperature': "{:.2f}".format(temp)} for hour, temp in zip(prediction_hours, predicted_temperatures)]}


    print(response)

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False, port=5002)
