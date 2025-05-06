import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state
if 'tippers' not in st.session_state:
    st.session_state.tippers = {
        'Tipper 1': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 2': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 3': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 4': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 5': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 6': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 7': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 8': {'kmr': 0, 'hmr': 0, 'last_service': None},
        'Tipper 9': {'kmr': 0, 'hmr': 0, 'last_service': None},
    }

# Tier conditions and service intervals
TIER_CONDITIONS = {
    'Tier 1': {
        'condition': "New or excellent condition (0-12 months)",
        'service_interval_kmr': 5000,
        'service_interval_hmr': 250,
        'replacement_threshold_kmr': 100000,
        'replacement_threshold_hmr': 5000
    },
    'Tier 2': {
        'condition': "Good condition (12-24 months)",
        'service_interval_kmr': 4500,
        'service_interval_hmr': 200,
        'replacement_threshold_kmr': 120000,
        'replacement_threshold_hmr': 6000
    },
    'Tier 3': {
        'condition': "Fair condition (24-36 months)",
        'service_interval_kmr': 4000,
        'service_interval_hmr': 150,
        'replacement_threshold_kmr': 150000,
        'replacement_threshold_hmr': 7500
    },
    'Tier 4': {
        'condition': "Needs attention (36+ months)",
        'service_interval_kmr': 3000,
        'service_interval_hmr': 100,
        'replacement_threshold_kmr': 200000,
        'replacement_threshold_hmr': 10000
    }
}

def update_tipper_data(tipper_name, kmr, hmr):
    st.session_state.tippers[tipper_name]['kmr'] += kmr
    st.session_state.tippers[tipper_name]['hmr'] += hmr
    st.success(f"Updated {tipper_name}: +{kmr} KMR, +{hmr} HMR")

def record_service(tipper_name):
    st.session_state.tippers[tipper_name]['last_service'] = datetime.now().date()
    st.success(f"Service recorded for {tipper_name} on {datetime.now().date()}")

def calculate_next_service(tipper_name, tier):
    if st.session_state.tippers[tipper_name]['last_service'] is None:
        return "No service history"
    
    last_service = st.session_state.tippers[tipper_name]['last_service']
    kmr_since_service = st.session_state.tippers[tipper_name]['kmr']
    hmr_since_service = st.session_state.tippers[tipper_name]['hmr']
    
    tier_data = TIER_CONDITIONS[tier]
    kmr_remaining = max(0, tier_data['service_interval_kmr'] - kmr_since_service)
    hmr_remaining = max(0, tier_data['service_interval_hmr'] - hmr_since_service)
    
    kmr_days = (kmr_remaining / (kmr_since_service / (datetime.now().date() - last_service).days)) if kmr_since_service > 0 else float('inf')
    hmr_days = (hmr_remaining / (hmr_since_service / (datetime.now().date() - last_service).days)) if hmr_since_service > 0 else float('inf')
    
    next_service_in = min(kmr_days, hmr_days)
    
    if next_service_in == float('inf'):
        return "Insufficient data to predict next service"
    
    next_service_date = datetime.now().date() + timedelta(days=int(next_service_in))
    return f"Next service due in ~{int(next_service_in)} days ({next_service_date})"

# App layout
st.title("Tipper Fleet Management System")

# Sidebar for navigation
menu = st.sidebar.selectbox("Menu", ["Daily Update", "Tier Details", "Service Schedule"])

if menu == "Daily Update":
    st.header("Daily KMR/HMR Update")
    
    selected_tipper = st.selectbox("Select Tipper", list(st.session_state.tippers.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        kmr = st.number_input("KMR to add", min_value=0, step=1)
    with col2:
        hmr = st.number_input("HMR to add", min_value=0, step=1)
    
    if st.button("Update Tipper"):
        update_tipper_data(selected_tipper, kmr, hmr)
    
    st.subheader("Current Tipper Status")
    tipper_df = pd.DataFrame.from_dict(st.session_state.tippers, orient='index')
    st.dataframe(tipper_df)

elif menu == "Tier Details":
    st.header("Tier Conditions and Specifications")
    
    selected_tier = st.selectbox("Select Tier", list(TIER_CONDITIONS.keys()))
    
    st.subheader("Tier Condition")
    st.write(TIER_CONDITIONS[selected_tier]['condition'])
    
    st.subheader("Service Intervals")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("KMR Interval", f"{TIER_CONDITIONS[selected_tier]['service_interval_kmr']} km")
    with col2:
        st.metric("HMR Interval", f"{TIER_CONDITIONS[selected_tier]['service_interval_hmr']} hours")
    
    st.subheader("Replacement Thresholds")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("KMR Replacement", f"{TIER_CONDITIONS[selected_tier]['replacement_threshold_kmr']} km")
    with col2:
        st.metric("HMR Replacement", f"{TIER_CONDITIONS[selected_tier]['replacement_threshold_hmr']} hours")

elif menu == "Service Schedule":
    st.header("Service Scheduling and Maintenance")
    
    selected_tipper = st.selectbox("Select Tipper", list(st.session_state.tippers.keys()))
    selected_tier = st.selectbox("Select Tier for this Tipper", list(TIER_CONDITIONS.keys()))
    
    st.subheader("Service Information")
    if st.session_state.tippers[selected_tipper]['last_service']:
        st.write(f"Last service: {st.session_state.tippers[selected_tipper]['last_service']}")
    else:
        st.warning("No service record found for this tipper")
    
    st.write(calculate_next_service(selected_tipper, selected_tier))
    
    if st.button("Record Service"):
        record_service(selected_tipper)
    
    st.subheader("Service Checklist")
    service_items = [
        "Engine oil change",
        "Oil filter replacement",
        "Air filter check/replacement",
        "Fuel filter replacement",
        "Coolant level check",
        "Brake system inspection",
        "Tire pressure and condition check",
        "Suspension inspection",
        "Lights and electrical check",
        "Hydraulic system check"
    ]
    
    for item in service_items:
        st.checkbox(item)
    
    st.subheader("Replacement Indicators")
    tipper_data = st.session_state.tippers[selected_tipper]
    tier_data = TIER_CONDITIONS[selected_tier]
    
    kmr_percent = (tipper_data['kmr'] / tier_data['replacement_threshold_kmr']) * 100
    hmr_percent = (tipper_data['hmr'] / tier_data['replacement_threshold_hmr']) * 100
    
    st.progress(min(100, kmr_percent), text=f"KMR: {tipper_data['kmr']}/{tier_data['replacement_threshold_kmr']} km")
    st.progress(min(100, hmr_percent), text=f"HMR: {tipper_data['hmr']}/{tier_data['replacement_threshold_hmr']} hours")
    
    if kmr_percent >= 100 or hmr_percent >= 100:
        st.error("This tipper has reached replacement threshold!")
