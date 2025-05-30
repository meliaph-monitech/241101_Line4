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

# Function to plot data with average by date
def plot_data(data, date_folders):
    for identifier, averages in data.items():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=date_folders, y=averages, mode='lines+markers', name=f'{identifier} Average'))

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

    # List and sort base folders
    base_folder = st.selectbox('Select Folder', list_folders(data_dir))
    
    if base_folder:
        # Load and aggregate data
        data, date_folders = load_and_aggregate_data(os.path.join(data_dir, base_folder))
        
        # Plot the aggregated data for each identifier
        plot_data(data, date_folders)
