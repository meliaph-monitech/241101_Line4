# -*- coding: utf-8 -*-
"""Bead Data Visualization in Streamlit"""

import streamlit as st
import pandas as pd
import zipfile
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page layout to wide (must be the first command)
st.set_page_config(layout="wide")

# Function to extract zip file
def extract_zip(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as z:
        z.extractall('data')
    return 'data'

# Function to list folders
def list_folders(path):
    return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])

# Function to load CSV files and aggregate data by date
def load_and_aggregate_data(path):
    date_data = {}
    date_folders = list_folders(path)

    for date_folder in date_folders:
        csv_files = [os.path.join(path, date_folder, f) for f in os.listdir(os.path.join(path, date_folder)) if f.endswith('.csv')]
        for csv_file in csv_files:
            df = pd.read_csv(csv_file, header=None)
            for identifier in ['Ch01', 'Ch02', 'Ch03']:
                subset = df[df[0] == identifier]
                if identifier not in date_data:
                    date_data[identifier] = {}
                # Store mean and std values for each date
                mean_value = subset.iloc[:, 1:].mean(axis=0).mean()
                std_value = subset.iloc[:, 1:].std(axis=0).mean()  # Standard deviation
                date_data[identifier][date_folder] = (mean_value, std_value)

    return date_data

# Function to plot mean and standard deviation in separate subplots for each channel
def plot_data(data_dict):
    for identifier in ['Ch01', 'Ch02', 'Ch03']:
        # Create a figure with two subplots
        fig = make_subplots(rows=2, cols=1, subplot_titles=(f'{identifier} Mean', f'{identifier} Standard Deviation'))

        # Get unique dates across all folders for the current identifier
        all_dates = sorted(set(date for folder_data in data_dict.values() for date in folder_data[identifier].keys()))

        for folder_name, folder_data in data_dict.items():
            y_mean = [folder_data[identifier].get(date, (None, None))[0] for date in all_dates]  # Mean values
            y_std = [folder_data[identifier].get(date, (None, None))[1] for date in all_dates]  # Std deviation values

            # Plot mean values on the first subplot
            fig.add_trace(go.Scatter(
                x=all_dates,
                y=y_mean,
                mode='lines+markers',
                name=f'Mean - {folder_name}'
            ), row=1, col=1)

            # Plot standard deviation values on the second subplot
            fig.add_trace(go.Scatter(
                x=all_dates,
                y=y_std,
                mode='lines+markers',
                name=f'Std Dev - {folder_name}',
                line=dict(dash='dash')  # Dashed line for standard deviation
            ), row=2, col=1)

        # Update layout for the figure
        fig.update_layout(
            title=f'{identifier} Bead Data',
            xaxis_title='Date',
            yaxis_title='Value',
            legend_title='Legend'
        )
        
        st.plotly_chart(fig)

# Streamlit UI
st.title('Bead Data Visualization (Averaged by Date and Standard Deviation)')

# File uploader
uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_file is not None:
    # Extract ZIP file
    data_dir = extract_zip(uploaded_file)

    # List base folders
    base_folders = list_folders(data_dir)
    selected_folders = st.multiselect('Select Folders', base_folders)

    if selected_folders:
        # Dictionary to hold data for each selected folder
        aggregated_data = {}

        for base_folder in selected_folders:
            # Load and aggregate data for the selected folder
            data = load_and_aggregate_data(os.path.join(data_dir, base_folder))
            aggregated_data[base_folder] = data
        
        # Plot the aggregated data for each identifier
        plot_data(aggregated_data)
