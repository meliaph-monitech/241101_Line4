# -*- coding: utf-8 -*-
"""Bead Data Visualization in Streamlit"""

import streamlit as st
import pandas as pd
import zipfile
import os
import plotly.graph_objects as go

# Set page layout to wide
st.set_page_config(layout="wide")

# Function to extract zip file
def extract_zip(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as z:
        z.extractall('data')
    return 'data'

# Function to list folders
def list_folders(path):
    return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])

# Function to load and aggregate CSV files from subdirectories
def load_and_aggregate_csv_files(path):
    data_frames = []

    # Iterate through each base folder and look for date-specific folders
    for folder in list_folders(path):
        date_folder_path = os.path.join(path, folder)

        # Get all date-specific folders
        date_folders = list_folders(date_folder_path)

        # Iterate through each date-specific folder to find CSV files
        for date_folder in date_folders:
            csv_file_path = os.path.join(date_folder_path, date_folder)
            csv_files = [os.path.join(csv_file_path, f) for f in os.listdir(csv_file_path) if f.endswith('.csv')]

            for csv_file in csv_files:
                try:
                    # Load the CSV file
                    df = pd.read_csv(csv_file, header=None)
                    # Assume the first column is the identifier and add a Date column based on the folder name
                    df['Date'] = date_folder  # Use the name of the date folder as the date
                    data_frames.append(df)
                except Exception as e:
                    st.error(f"Error reading {csv_file}: {e}")

    # Concatenate all data frames
    if data_frames:
        full_data = pd.concat(data_frames, ignore_index=True)
        return full_data
    else:
        st.warning("No valid data frames to concatenate.")
        return pd.DataFrame()  # Return an empty DataFrame if no valid data frames

# Function to plot data aggregated by date
def plot_data_aggregated_by_date(full_data):
    fig = go.Figure()

    # Get the unique dates from the data
    unique_dates = full_data['Date'].unique()
    
    # Iterate over the channel identifiers (Ch01, Ch02, Ch03)
    for identifier in ['Ch01', 'Ch02', 'Ch03']:
        # Filter data for the specified identifier
        subset = full_data[full_data[0] == identifier]

        # Check if the subset is empty
        if subset.empty:
            st.warning(f"No data found for {identifier}.")
            continue

        # Ensure we only aggregate numeric columns, excluding the identifier and Date columns
        numeric_columns = subset.iloc[:, 1:-1]  # Exclude the first column (identifier) and the last (Date)

        # Group by date and calculate mean for each date
        if not numeric_columns.empty:
            mean_values = numeric_columns.groupby(subset['Date']).mean()
            mean_values = mean_values.reset_index()  # Reset index to get 'Date' back as a column

            # Get the dates and mean values for plotting
            dates = mean_values['Date']
            means = mean_values.drop(columns=['Date']).mean(axis=1)  # Average across beads for each date

            # Plot data
            fig.add_trace(go.Scatter(x=dates, y=means, mode='lines+markers', name=f'{identifier} Mean'))
        else:
            st.warning(f"No numeric data found for {identifier}.")

    fig.update_layout(
        title='Bead Data (Averaged by Date)',
        xaxis_title='Date',
        yaxis_title='Average Value',
        xaxis=dict(type='category')  # Ensure X-axis treats dates as categories
    )
    st.plotly_chart(fig)

# Streamlit UI
st.title('Bead Data Visualization (Averaged by Date)')

# File uploader
uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_file is not None:
    # Extract ZIP file
    data_dir = extract_zip(uploaded_file)
    
    # List and sort base folders
    base_folder = st.selectbox('Select Folder', list_folders(data_dir))
    
    if base_folder:
        # Load and aggregate data from all CSV files in the selected base folder's subdirectories
        full_data = load_and_aggregate_csv_files(os.path.join(data_dir, base_folder))
        
        # Plot the aggregated data
        plot_data_aggregated_by_date(full_data)
