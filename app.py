import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Initialize session state
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = pd.DataFrame(columns=[
        'VehicleID', 'LastServiceDate', 'CurrentHMR', 'CurrentKMR',
        'NextService', 'ServiceType', 'NotificationSent'
    ])

# Service intervals dictionary
service_intervals = {
    'Engine Oil': {'hours': 1000, 'km': 15000, 'months': 18},
    'Cooling System': {'hours': 5000, 'km': 75000, 'months': 36},
    # Add all other services similarly
}

def calculate_next_service(last_service, current_hmr, current_kmr, service_type):
    interval = service_intervals[service_type]
    next_service = {}
    
    if 'hours' in interval:
        next_service['hmr'] = last_service['hmr'] + interval['hours'] * 0.9
    if 'km' in interval:
        next_service['kmr'] = last_service['kmr'] + interval['km'] * 0.9
    if 'months' in interval:
        next_service['date'] = last_service['date'] + timedelta(days=interval['months']*30*0.9)
    
    return next_service

def check_service_due(vehicle):
    alerts = []
    for service, interval in service_intervals.items():
        # Check hours
        if 'hours' in interval and (vehicle['CurrentHMR'] >= vehicle[f'{service}_NextHMR']):
            alerts.append(f"{service} due by hours")
        # Check km
        if 'km' in interval and (vehicle['CurrentKMR'] >= vehicle[f'{service}_NextKMR']):
            alerts.append(f"{service} due by km")
        # Check date
        if 'months' in interval and (datetime.now() >= vehicle[f'{service}_NextDate']):
            alerts.append(f"{service} due by time")
    return alerts

# Streamlit UI
st.title('Tipper Fleet Maintenance Management')

tab1, tab2, tab3 = st.tabs(["Dashboard", "Add/Update Vehicle", "Service Records"])

with tab1:
    st.header("Maintenance Alerts")
    if not st.session_state.vehicles.empty:
        for idx, vehicle in st.session_state.vehicles.iterrows():
            alerts = check_service_due(vehicle)
            if alerts:
                st.warning(f"Vehicle {vehicle['VehicleID']} has due services:")
                for alert in alerts:
                    st.write(f"- {alert}")
            else:
                st.success(f"Vehicle {vehicle['VehicleID']} - All services up to date")
    else:
        st.info("No vehicles in the system")

with tab2:
    st.header("Add or Update Vehicle Information")
    with st.form("vehicle_form"):
        vid = st.text_input("Vehicle ID")
        service_date = st.date_input("Last Service Date")
        hmr = st.number_input("Current HMR", min_value=0)
        kmr = st.number_input("Current KMR", min_value=0)
        service_type = st.selectbox("Service Type", list(service_intervals.keys()))
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Update or add vehicle data
            pass

with tab3:
    st.header("Service History")
    # Display service records
