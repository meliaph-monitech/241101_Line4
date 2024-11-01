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
                    date_data[identifier] = []
                date_data[identifier].append(subset.iloc[:, 1:].mean(axis=0))  # Aggregate means by bead number

    # Convert lists of means to averages by date
    for identifier in date_data:
        date_data[identifier] = pd.DataFrame(date_data[identifier]).mean(axis=0)  # Average across all date-specific means
    return date_data, date_folders

# Function to create standardized date range and align data
def align_data_to_dates(data_dict):
    all_dates = [str(i).zfill(2) for i in range(1, 32)]  # Dates from 01 to 31
    aligned_data = {}

    for folder_name, data in data_dict.items():
        aligned_data[folder_name] = {}
        for identifier in ['Ch01', 'Ch02', 'Ch03']:
            # Create a DataFrame to hold aligned data
            averages = pd.Series(data[identifier])
            # Align averages to the date range, filling missing values with NaN
            aligned_data[folder_name][identifier] = averages.reindex(all_dates, fill_value=None)

    return aligned_data, all_dates

# Function to plot data with average by date for multiple folders
def plot_data(data_dict, all_dates):
    for identifier in ['Ch01', 'Ch02', 'Ch03']:
        fig = go.Figure()

        for folder_name, averages in data_dict.items():
            fig.add_trace(go.Scatter(x=all_dates, y=averages[identifier], mode='lines+markers', name=f'{identifier} - {folder_name}'))

        fig.update_layout(
            title=f'{identifier} Bead Data (Averaged by Date)',
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

    # List base folders
    base_folders = list_folders(data_dir)
    selected_folders = st.multiselect('Select Folders', base_folders)

    if selected_folders:
        # Dictionary to hold data for each selected folder
        aggregated_data = {}

        for base_folder in selected_folders:
            # Load and aggregate data for the selected folder
            data, date_folders = load_and_aggregate_data(os.path.join(data_dir, base_folder))
            aggregated_data[base_folder] = data
        
        # Align data to the standardized date range
        aligned_data, all_dates = align_data_to_dates(aggregated_data)
        
        # Plot the aggregated data for each identifier
        plot_data(aligned_data, all_dates)
