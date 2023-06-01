import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from math import sqrt
import time

start_time = time.time()

# Load preprocessed data
excel_file_path = "./dataset/input/refined_data_all.xlsx"
df = pd.read_excel(excel_file_path)

# Define features and target variable
features = ['YEAR', 'MONTH', 'DAY', 'HOUR', 'DAY_OF_THE_WEEK', 'IS_HOLIDAY', 'TEMPERATURE']
X = df[features]
y = df['ELECTRICITY']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Drop rows with missing values
X_train = X_train.dropna()
y_train = y_train.loc[X_train.index]  # Update y_train accordingly
X_test = X_test.dropna()
y_test = y_test.loc[X_test.index]  # Update y_test accordingly

def train_linear_regression(X_train, y_train):
    return LinearRegression().fit(X_train, y_train)

def train_knn(X_train, y_train, n_neighbors=5):
    n_neighbors = min(n_neighbors, len(X_train))
    return KNeighborsRegressor(n_neighbors=n_neighbors).fit(X_train, y_train)

def train_xgboost(X_train, y_train):
    return XGBRegressor().fit(X_train, y_train)

def predict(model, X_test):
    return model.predict(X_test)

def calculate_metrics(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = sqrt(mse)
    r_squared = r2_score(y_true, y_pred)
    return mse, rmse, r_squared

def evaluate_models(models, X_test, y_test):
    results = {}
    for name, model in models.items():
        y_pred = predict(model, X_test)
        mse, rmse, r_squared = calculate_metrics(y_test, y_pred)
        results[name] = {'MSE': mse, 'RMSE': rmse, 'r2_score': r_squared}
    return results

def save_true_predicted_values(models, X_test, y_test, file_path="./dataset/output/true_predicted_values.xlsx"):
    result_df = pd.DataFrame({'True (MegaWatt)': y_test})
    for name, model in models.items():
        y_pred = predict(model, X_test)
        result_df[f'{name}_P (MegaWatt)'] = y_pred
    result_df.to_excel(file_path, index=False)

# Train linear regression, KNN, XGBoost models
models = {}
models['linear_regression'] = train_linear_regression(X_train, y_train)
models['knn'] = train_knn(X_train, y_train)
models['xgboost'] = train_xgboost(X_train, y_train)

# Evaluate models and save results
results = evaluate_models(models, X_test, y_test)
df_evaluation_metric = pd.DataFrame(results)
print(df_evaluation_metric)

# Save the metrics to an Excel file
df_evaluation_metric.to_excel("./dataset/input/metrics.xlsx", index=True)

# Save true and predicted values to an Excel file with MegaWatt unit
save_true_predicted_values(models, X_test, y_test)

print('Last part executed.')

# Calculate processing time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Processing time: {elapsed_time} seconds")
