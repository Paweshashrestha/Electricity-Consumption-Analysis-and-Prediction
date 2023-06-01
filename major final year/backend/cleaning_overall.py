import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Cleaning process without outlier removal

df = pd.read_excel("./dataset/input/final dataset.xlsx", parse_dates=["DATE"]) # Loading excel file

# Dropping duplicates
df_all = df.drop_duplicates().copy()  # Create a copy for saving all steps

# Cubic spline interpolation to fill missing elements
consumption = ['ELECTRICITY'] 

for column_name in consumption:
    # Missing indices
    missing_indices = df_all[df_all[column_name].isnull()].index

    # Non-missing indices and values
    non_missing_indices = df_all[~df_all[column_name].isnull()].index
    non_missing_values = df_all.loc[non_missing_indices, column_name]

    # Handle non-finite values
    non_finite_mask = ~np.isfinite(non_missing_values)
    if np.any(non_finite_mask):
        # Handle non-finite values
        non_missing_values[non_finite_mask] = non_missing_values.mean()

    # Perform cubic spline interpolation
    cs = CubicSpline(non_missing_indices, non_missing_values, bc_type='natural')

    # Interpolate missing values
    interpolated_values = cs(missing_indices)

    # Two decimal places rounding
    interpolated_values = np.round(interpolated_values, 2)

    # Update the DataFrame with interpolated values
    df_all.loc[missing_indices, column_name] = interpolated_values

# print('Interpolation done')


# Convert the 'YEAR' column to string in "yyyy" format before saving
df_all['YEAR'] = df_all['YEAR'].astype(str)

# Save the DataFrame after all steps before outlier removal
df_all['DATE'] = df_all['DATE'].dt.strftime('%Y-%m-%d')

# Save the DataFrame after all steps before outlier removal
excel_file_path_all = "./dataset/input/refined_data_all.xlsx"
df_all.to_excel(excel_file_path_all, index=False)

# Box plot before outlier removal
columns_names = ['ELECTRICITY']

for column_name in columns_names:
    plt.figure(figsize=(8, 6))  # Adjust figure size
    plt.subplot(1, 2, 1)
    df_all[[column_name]].boxplot()
    plt.title(f'Box Plot for Column {column_name} (Before Outlier Removal)')

# Remove outliers based on box plot
for column_name in consumption:
    # Calculate IQR
    Q1 = df_all[column_name].quantile(0.25)
    print("Q1:", Q1)  # Print the first quartile
   
    Q3 = df_all[column_name].quantile(0.75)
   
    IQR = Q3 - Q1

    # Define lower and upper bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    df_all = df_all[(df_all[column_name] >= lower_bound) & (df_all[column_name] <= upper_bound)]

# Box plot after outlier removal
for column_name in columns_names:
    plt.subplot(1, 2, 2)
    df_all[[column_name]].boxplot()
    plt.title(f'Box Plot for Column {column_name} (After Outlier Removal)')

plt.tight_layout()
plt.show()

# Save cleaned file after outlier removal
excel_file_path_outlier_removed = "./dataset/input/refined_data_outlier_removed.xlsx"
df_all.to_excel(excel_file_path_outlier_removed, index=False)

# Check if the code executed successfully
# print('Success')