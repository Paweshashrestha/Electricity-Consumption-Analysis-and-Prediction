import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from math import sqrt
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score, KFold
import time
start_time = time.time() 




# Load preprocessed data
excel_file_path = "/Users/paweshashrestha/Downloads/major_final 2/cleaned files/refined_data_all.xlsx"
df = pd.read_excel(excel_file_path)

# Define features and target variable
features = ['YEAR', 'MO', 'DY', 'HR', 'DOTW', 'IS_HOLIDAY', 'T2M']
X = df[features]
y = df['electricity']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

def train_linear_regression(X_train, y_train):
    return LinearRegression().fit(X_train, y_train)

def train_knn(X_train, y_train, n_neighbors=5):
    n_neighbors = min(n_neighbors, len(X_train))
    return KNeighborsRegressor(n_neighbors=n_neighbors).fit(X_train, y_train)

def train_xgboost(X_train, y_train):
    return XGBRegressor().fit(X_train, y_train)

def train_svm(X_train, y_train):
    model = SVR(kernel='poly', C=1000, degree=12)
    return model.fit(X_train, y_train)

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

def save_true_predicted_values(models, X_test, y_test, file_path="/Users/paweshashrestha/Downloads/major_final 2/true.xlsx"):
    result_df = pd.DataFrame({'True': y_test})
    for name, model in models.items():
        y_pred = predict(model, X_test)
        result_df[f'{name}_P'] = y_pred
    result_df.to_excel(file_path, index=False)

# Train linear regression, KNN, XGBoost models
models = {}
models['linear_regression'] = train_linear_regression(X_train, y_train)
models['knn'] = train_knn(X_train, y_train)
models['xgboost'] = train_xgboost(X_train, y_train)
models['svm'] = train_svm(X_train, y_train)

# Specify the range of dates for prediction
start_date = pd.Timestamp('2080-01-01')  # Specify the start date
end_date = pd.Timestamp('2080-01-15')    # Specify the end date
date_range = pd.date_range(start_date, end_date, freq='H')  # Adjust the frequency as needed

# Predict electricity demand for each date in the range
predictions = {}
for specific_date in date_range:
    specific_day = pd.DataFrame({
        'YEAR': [specific_date.year] * 24,
        'MO': [specific_date.month] * 24,
        'DY': [specific_date.day] * 24,
        'HR': range(24),
        'DOTW': [specific_date.dayofweek + 1] * 24,  # Day of the week (e.g., Monday)
        'IS_HOLIDAY': [0] * 24,  # 0 or 1 indicating if it's a holiday
        'T2M': [25.5] * 24  # Replace with the temperature for that day
    })
    print(f"\nDate: {specific_date.strftime('%Y-%m-%d')}")
    for hour in range(24):
        print(f"{hour + 1}:")
        for name, model in models.items():
            prediction = predict(model, specific_day)
            print(f"   {name}: {prediction[hour]}")

    predictions[specific_date] = {}
    for name, model in models.items():
        predictions[specific_date][name] = predict(model, specific_day)

# Rest of your code...



 
# Perform cross-validation with the best model
 
k_fold = KFold(n_splits=5, shuffle=True, random_state=42)
cross_val_scores = cross_val_score(models['svm'], X_train, y_train, cv=k_fold, scoring='neg_mean_squared_error', n_jobs=-1)
print("Cross-Validation Scores:", -cross_val_scores)
print("Mean Cross-Validation RMSE:", -cross_val_scores.mean())
 
 
results = evaluate_models(models, X_test, y_test)
df_evaluation_metric = pd.DataFrame(results)
print(df_evaluation_metric)
 
# Save the DataFrame to an Excel file
df_evaluation_metric.to_excel("/Users/paweshashrestha/Downloads/major_final 2/metrics.xlsx", index=True)
 
# Save true and predicted values to an Excel file
save_true_predicted_values(models,X_test, y_test)
 
print('Last part executed.')
 
#asti processing time sodheko thyo so haldeko hai herna lai
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Processing time: {elapsed_time} seconds")
 
print(predictions)