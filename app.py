import streamlit as st
import pandas as pd
from datetime import datetime

# Load data function (in a real app, you'd load from Excel/DB)
def load_tipper_data():
    # This is a simplified version - in reality you'd load from the Excel file
    data = {
        'Asst.No: / Door No.': ['AL-1', 'AL-2', 'AL-3', 'AL-4', 'AL-5', 'AL-6', 'AL-7', 'AL-8', 'AL-9'],
        'EQUIPMENT': ['TIPPER - 1', 'TIPPER - 2', 'TIPPER - 3', 'TIPPER - 4', 'TIPPER - 5', 'TIPPER - 6', 'TIPPER - 7', 'TIPPER - 8', 'TIPPER - 9'],
        'M/c Sr.No: / Reg No:': ['AP39UQ0095', 'AP39UQ0097', 'AP39UW9881', 'AP39UW9880', 'AP39UY4651', 'AP39UY4652', 'AP39WC0926', 'AP39WC0927', 'AP39WC0928'],
        'Commissioning Date': ['-', '-', '-', '-', '2024-08-30', '2024-08-30', '2025-02-14', '2025-02-14', '2025-02-14'],
        'Current HMR': [5105.3, 5202.8, 2547, 2300, 1540, 1157, 0, 0, 0],
        'Last Service Date': ['2025-04-16', '2025-04-16', '2025-04-08', '2025-03-15', '2025-03-20', '2025-01-25', '2025-02-14', '2025-02-14', '2025-02-14'],
        'Next Engine Oil Change': [6105.3, 6202.8, 3547, 3300, 2540, 2157, 1000, 1000, 1000],
        'Next Air Filter Change': [7105.3, 7202.8, 4547, 4300, 3540, 3157, 2000, 2000, 2000],
        'Status': ['Operational', 'Operational', 'Operational', 'Operational', 'Operational', 'Operational', 'New', 'New', 'New']
    }
    return pd.DataFrame(data)

def main():
    st.set_page_config(page_title="Tipper Maintenance Tracker", layout="wide")
    
    st.title("Tipper Periodic Maintenance Tracker")
    st.subheader("Angul Coal Mines - Mythri Infrastructure & Mining India Pvt Ltd")
    
    # Load data
    df = load_tipper_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    status_filter = st.sidebar.selectbox("Status", ["All", "Operational", "New"])
    due_filter = st.sidebar.checkbox("Show only due for service")
    
    # Apply filters
    if status_filter != "All":
        df = df[df['Status'] == status_filter]
    
    # Main display
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Tipper Fleet Overview")
        
        # Display data table
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Detailed view for selected tipper
        st.subheader("Tipper Details")
        selected_tipper = st.selectbox("Select Tipper", df['Asst.No: / Door No.'])
        
        tipper_details = df[df['Asst.No: / Door No.'] == selected_tipper].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Asset Number", tipper_details['Asst.No: / Door No.'])
            st.metric("Registration", tipper_details['M/c Sr.No: / Reg No:'])
            st.metric("Current HMR", tipper_details['Current HMR'])
            
        with col2:
            st.metric("Commission Date", tipper_details['Commissioning Date'])
            st.metric("Last Service", tipper_details['Last Service Date'])
            st.metric("Next Oil Change Due", tipper_details['Next Engine Oil Change'])
        
        # Maintenance history (would come from database in real app)
        st.subheader("Maintenance History")
        st.write("""
        | Service Type       | Date       | HMR    | Next Due HMR |
        |--------------------|------------|--------|--------------|
        | Engine Oil Change  | 2025-04-16 | 5105.3 | 6105.3       |
        | Air Filter Change  | 2025-01-10 | 4800   | 7105.3       |
        | Brake Inspection  | 2024-12-15 | 4500   | 6500         |
        """)
    
    with col2:
        st.subheader("Maintenance Alerts")
        
        # Sample alerts (would be calculated in real app)
        alert_data = [
            {"Tipper": "AL-1", "Service": "Engine Oil Change", "Due HMR": 6105.3, "Current HMR": 5105.3, "Remaining": 1000},
            {"Tipper": "AL-2", "Service": "Transmission Oil", "Due HMR": 5202.8, "Current HMR": 5202.8, "Remaining": 0},
            {"Tipper": "AL-3", "Service": "Air Filter", "Due HMR": 3547, "Current HMR": 2547, "Remaining": 1000}
        ]
        
        for alert in alert_data:
            with st.expander(f"{alert['Tipper']} - {alert['Service']}"):
                st.metric("Due At", alert['Due HMR'])
                st.metric("Current HMR", alert['Current HMR'])
                st.metric("Remaining", alert['Remaining'])
                if st.button("Mark as Complete", key=f"complete_{alert['Tipper']}_{alert['Service']}"):
                    st.success(f"Service recorded for {alert['Tipper']}")
        
        st.subheader("Quick Actions")
        if st.button("Generate Monthly Report"):
            st.info("Monthly maintenance report generated")
        if st.button("Request Parts Order"):
            st.info("Parts order request submitted")
    
    # Maintenance form
    st.subheader("Record Maintenance")
    with st.form("maintenance_form"):
        tipper = st.selectbox("Tipper", df['Asst.No: / Door No.'])
        service_type = st.selectbox("Service Type", [
            "Engine Oil Change", 
            "Air Filter Change", 
            "Transmission Service",
            "Brake Inspection",
            "Coolant Change",
            "Other"
        ])
        service_date = st.date_input("Service Date", datetime.today())
        hmr = st.number_input("HMR at Service", min_value=0.0)
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Record Service")
        if submitted:
            st.success(f"Recorded {service_type} for {tipper} on {service_date} at HMR {hmr}")

if __name__ == "__main__":
    main()
