import streamlit as st
import os
import pandas as pd
import zipfile
import matplotlib.pyplot as plt

# Function to extract ZIP files
def extract_zip(uploaded_zip):
    with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
        zip_ref.extractall('/content/temp_data')  # Specify a temporary extraction path

# Function to plot aggregated data from selected category folder, separated by channels
def plot_aggregated_data(folder_path):
    # Initialize a dictionary to store aggregated data for each channel
    aggregated_data = {
        'Ch01': pd.DataFrame(),
        'Ch02': pd.DataFrame(),
        'Ch03': pd.DataFrame()
    }

    # Process each date-specific folder in the selected category folder
    for date_folder in os.listdir(folder_path):
        date_folder_path = os.path.join(folder_path, date_folder)
        if os.path.isdir(date_folder_path):  # Ensure it's a directory
            for file in os.listdir(date_folder_path):
                if file.endswith('.csv'):
                    file_path = os.path.join(date_folder_path, file)
                    df = pd.read_csv(file_path)

                    # Assuming the first column contains dates in a standard format
                    # Convert the first column to datetime if necessary
                    if pd.api.types.is_string_dtype(df.iloc[:, 0]):
                        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])

                    # Separate data into channels
                    for channel in ['Ch01', 'Ch02', 'Ch03']:
                        if channel in df.columns:
                            channel_data = df[[df.columns[0], channel]].rename(columns={df.columns[0]: 'Date'})
                            aggregated_data[channel] = pd.concat([aggregated_data[channel], channel_data], ignore_index=True)

    # Plotting the aggregated data for each channel
    plt.figure(figsize=(12, 6))
    for channel, data in aggregated_data.items():
        # Sort data by date
        data = data.sort_values(by='Date')
        plt.plot(data['Date'], data[channel], label=channel)

    plt.title('Aggregated Signal Data Over Time by Channel')
    plt.xlabel('Date')
    plt.ylabel('Signal Values')
    plt.legend(title='Channels')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Streamlit app setup
st.title('Signal Data Visualization from NIR and VIS Signals')

# Upload ZIP file
uploaded_zip = st.file_uploader("Upload a ZIP file containing the data", type=["zip"])

if uploaded_zip:
    # Extract ZIP file
    extract_zip(uploaded_zip)
    st.success("ZIP file extracted successfully!")

    # Select category folder
    selected_category = st.selectbox("Select a category", list(directories.keys()))

    # Plot the aggregated data
    plot_aggregated_data(directories[selected_category])
