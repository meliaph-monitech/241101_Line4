# -*- coding: utf-8 -*-
"""Bead Data Visualization in Streamlit - Aggregated by Folder"""

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

# Function to load all CSV files from a specified path
def load_all_csv_files(path):
    all_data = []
    # Iterate through each date-specific folder in the selected base folder
    for date_folder in list_folders(path):
        folder_path = os.path.join(path, date_folder)
        csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, header=None)
            # Add a new column for the date
            df['Date'] = date_folder  # Assuming date is the folder name
            all_data.append(df)
    
    # Concatenate all dataframes into one
    return pd.concat(all_data, ignore_index=True)

# Function to plot aggregated data by date for each identifier
def plot_aggregated_data(df, identifier):
    fig = go.Figure()

    # Filter data for the specified identifier (e.g., Ch01, Ch02, Ch03)
    subset = df[df[0] == identifier]
    
    # Group by Date and calculate mean values
    means = subset.groupby('Date').mean().reset_index()
    
    # Plot data
    fig.add_trace(go.Scatter(x=means['Date'], y=means.iloc[:, 1:], mode='lines+markers', name=f'{identifier} Mean'))

    fig.update_layout(
        title=f'{identifier} Bead Data (Aggregated by Date)',
        xaxis_title='Date',
        yaxis_title='Average Value',
        xaxis_tickangle=-45  # Optional: Tilt x-axis labels for better readability
    )
    st.plotly_chart(fig)

# Streamlit UI
st.title('Bead Data Visualization (Aggregated by Folder)')

# File uploader
uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_file is not None:
    # Extract ZIP file
    data_dir = extract_zip(uploaded_file)
    
    # List and sort base folders
    base_folder = st.selectbox('Select Folder', list_folders(data_dir))
    
    if base_folder:
        # Load and aggregate data from all CSV files in the selected base folder
        df = load_all_csv_files(os.path.join(data_dir, base_folder))
        
        for identifier in ['Ch01', 'Ch02', 'Ch03']:
            st.subheader(f'Plot for {identifier}')
            plot_aggregated_data(df, identifier)
