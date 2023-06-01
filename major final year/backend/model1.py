import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR
from sklearn.impute import SimpleImputer
from math import sqrt
import time

start_time = time.time()

# Load preprocessed data
excel_file_path = "./dataset/input/final dataset.xlsx"
df = pd.read_excel(excel_file_path, parse_dates=['DATE'])  # Specify 'DATE' column as datetime
# Print column names
print("Column names in DataFrame:", df.columns)

# Filter data based on date range
start_date = '2078-01-01'
end_date = '2080-08-30'
df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

print("Number of samples after filtering:", df.shape[0])

# Check if there are sufficient samples
if df.shape[0] > 0:
    # Define features and target variable
    features = ['YEAR\n', 'MONTH', 'DAY', 'HOUR', 'DOTW', 'IS_HOLIDAY', 'T2M']

    X = df[features]
    y = df['electricity']

    # Handle missing values using SimpleImputer
    imputer = SimpleImputer(strategy='mean')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=features)

    # Concatenate the imputed features and the 'DATE' column
    X = pd.concat([X_imputed, df['DATE']], axis=1)

    # Sort data by date
    X = X.sort_values(by='DATE')

    # Define the percentage for training data
    train_percentage = 0.8
    split_index = int(train_percentage * len(X))

    # Split data into training and testing sets
    X_train, X_test = X.iloc[:split_index].drop(columns=['DATE']), X.iloc[split_index:].drop(columns=['DATE'])
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    # Print start and end dates of training and testing sets
    print("Training Start Date:", X.iloc[:split_index]['DATE'].min())
    print("Training End Date:", X.iloc[:split_index]['DATE'].max())
    print("Testing Start Date:", X.iloc[split_index:]['DATE'].min())
    print("Testing End Date:", X.iloc[split_index:]['DATE'].max())

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

    def save_true_predicted_values(models, X_test, y_test, file_path):
        result_df = pd.DataFrame({'True': y_test})
        for name, model in models.items():
            y_pred = predict(model, X_test)
            result_df[f'{name}_P'] = y_pred
        result_df.to_excel(file_path, index=False)

    # Train linear regression, KNN, XGBoost, SVM models
    models = {}
    models['linear_regression'] = train_linear_regression(X_train, y_train)
    models['knn'] = train_knn(X_train, y_train)
    models['xgboost'] = train_xgboost(X_train, y_train)
    models['svm'] = train_svm(X_train, y_train)

    # Perform cross-validation with the best model (using TimeSeriesSplit)
    tscv = TimeSeriesSplit(n_splits=5)
    cross_val_scores = cross_val_score(models['svm'], X_train, y_train, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
    print("Cross-Validation Scores:", -cross_val_scores)
    print("Mean Cross-Validation RMSE:", -cross_val_scores.mean())

    results = evaluate_models(models, X_test, y_test)
    df_evaluation_metric = pd.DataFrame(results)
    print(df_evaluation_metric)

    # Save the DataFrame to an Excel file
    df_evaluation_metric.to_excel("./dataset/output/metrics.xlsx", index=False)

    # Save true and predicted values to an Excel file
    save_true_predicted_values(models, X_test, y_test, "/Users/kumudshrestha/Downloads/major_final_pre/true_predicted_values.xlsx")

    print('Last part executed.')

    # Display processing time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing time: {elapsed_time} seconds")
else:
    print("Insufficient samples after filtering. Check your date range.")
