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
    dates = []

    # Iterate through each base folder and look for date-specific folders
    for folder in list_folders(path):
        date_folder_path = os.path.join(path, folder)

        # Get all CSV files from the date-specific folders
        csv_files = [os.path.join(date_folder_path, f) for f in os.listdir(date_folder_path) if f.endswith('.csv')]
        
        if not csv_files:
            st.warning(f"No CSV files found in folder: {date_folder_path}")
            continue

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, header=None)
                date_str = os.path.basename(date_folder_path)  # Use the name of the date folder as the date
                df['Date'] = date_str  # Add a Date column based on the folder name
                data_frames.append(df)
                dates.append(date_str)
            except Exception as e:
                st.error(f"Error reading {csv_file}: {e}")

    # Concatenate all data frames
    if data_frames:
        full_data = pd.concat(data_frames, ignore_index=True)
        return full_data, sorted(set(dates))
    else:
        st.warning("No valid data frames to concatenate.")
        return pd.DataFrame(), []  # Return an empty DataFrame if no valid data frames

# Function to plot data aggregated by date
def plot_data_aggregated_by_date(full_data):
    fig = go.Figure()

    # Iterate over the channel identifiers (Ch01, Ch02, Ch03)
    for identifier in ['Ch01', 'Ch02', 'Ch03']:
        # Filter data for the specified identifier
        subset = full_data[full_data[0] == identifier]

        # Group by date and calculate mean for each date
        mean_values = subset.groupby('Date').mean().iloc[:, 1:]  # Exclude the identifier column
        
        # Get the dates and mean values for plotting
        dates = mean_values.index
        means = mean_values.values.flatten()

        # Plot data
        fig.add_trace(go.Scatter(x=dates, y=means, mode='lines+markers', name=f'{identifier} Mean'))

    fig.update_layout(
        title='Bead Data (Averaged by Date)',
        xaxis_title='Date',
        yaxis_title='Average Value'
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
        full_data, _ = load_and_aggregate_csv_files(os.path.join(data_dir, base_folder))
        
        # Plot the aggregated data
        plot_data_aggregated_by_date(full_data)
