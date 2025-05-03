import streamlit as st
import pandas as pd
from datetime import datetime

# Set page title and layout
st.set_page_config(page_title="Blasting Tracker", layout="wide")

# Title
st.title("Blasting Equipment Tracker")

# Initialize session state for data storage
if 'blasting_data' not in st.session_state:
    st.session_state.blasting_data = pd.DataFrame(columns=[
        'Date', 'Total_Compressors', 'Compressors_Used', 'Compressors_Remaining'
    ])

# Sidebar for adding new entries
with st.sidebar:
    st.header("Add New Entry")
    
    # Input fields
    entry_date = st.date_input("Date", datetime.today())
    total_compressors = st.number_input("Total Compressors Available", min_value=1, value=1)
    compressors_used = st.number_input("Compressors Used", min_value=0, max_value=total_compressors, value=0)
    
    # Calculate remaining
    compressors_remaining = total_compressors - compressors_used
    
    # Add button
    if st.button("Add Entry"):
        new_entry = {
            'Date': entry_date,
            'Total_Compressors': total_compressors,
            'Compressors_Used': compressors_used,
            'Compressors_Remaining': compressors_remaining
        }
        
        # Add to DataFrame
        st.session_state.blasting_data = pd.concat([
            st.session_state.blasting_data,
            pd.DataFrame([new_entry])
        ], ignore_index=True)
        
        st.success("Entry added successfully!")

# Main content area
st.header("Blasting Records")

# Display data table
if not st.session_state.blasting_data.empty:
    # Sort by date
    df_sorted = st.session_state.blasting_data.sort_values('Date', ascending=False)
    
    # Display table
    st.dataframe(df_sorted, use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Entries", len(df_sorted))
    
    with col2:
        avg_usage = df_sorted['Compressors_Used'].mean()
        st.metric("Average Compressors Used", f"{avg_usage:.1f}")
    
    with col3:
        total_available = df_sorted['Total_Compressors'].sum()
        total_used = df_sorted['Compressors_Used'].sum()
        utilization = (total_used / total_available) * 100 if total_available > 0 else 0
        st.metric("Total Utilization Rate", f"{utilization:.1f}%")
    
    # Data visualization
    st.subheader("Usage Over Time")
    df_sorted['Date'] = pd.to_datetime(df_sorted['Date'])
    df_sorted = df_sorted.set_index('Date').sort_index()
    
    tab1, tab2 = st.tabs(["Line Chart", "Bar Chart"])
    
    with tab1:
        st.line_chart(df_sorted[['Compressors_Used', 'Compressors_Remaining']])
    
    with tab2:
        st.bar_chart(df_sorted[['Compressors_Used', 'Compressors_Remaining']])
    
    # Data export
    st.subheader("Data Export")
    csv = df_sorted.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name='blasting_records.csv',
        mime='text/csv'
    )
else:
    st.info("No entries yet. Add your first entry using the sidebar.")

# Optional: Add data clearing functionality
if st.button("Clear All Data", type="secondary"):
    st.session_state.blasting_data = pd.DataFrame(columns=[
        'Date', 'Total_Compressors', 'Compressors_Used', 'Compressors_Remaining'
    ])
    st.rerun()
