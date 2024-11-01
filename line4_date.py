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

# Function to load and aggregate CSV files
def load_and_aggregate_csv_files(path):
    csv_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    data_frames = []
    dates = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, header=None)
        date_str = os.path.basename(csv_file).split('.')[0]  # Extract date from filename
        df['Date'] = date_str  # Add a Date column based on the filename
        data_frames.append(df)
        dates.append(date_str)

    # Concatenate all data frames
    full_data = pd.concat(data_frames, ignore_index=True)
    return full_data, sorted(set(dates))

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
        # Load and aggregate data from all CSV files in the selected base folder
        full_data, _ = load_and_aggregate_csv_files(os.path.join(data_dir, base_folder))
        
        # Plot the aggregated data
        plot_data_aggregated_by_date(full_data)
