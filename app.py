import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load the data
data = {
    "SL NO": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "Asst.No": ["AL-1", "AL-2", "AL-3", "AL-4", "AL-5", "AL-6", "AL-7", "AL-8", "AL-9"],
    "Equipment": ["TIPPER - 1", "TIPPER - 2", "TIPPER - 3", "TIPPER - 4", "TIPPER - 5", "TIPPER - 6", "TIPPER - 7", "TIPPER - 8", "TIPPER - 9"],
    "M/c Sr.No": ["AP39UQ0095", "AP39UQ0097", "AP39UW9881", "AP39UW9880", "AP39UY4651", "AP39UY4652", "AP39WC0926", "AP39WC0927", "AP39WC0928"],
    "Commissioning Date": ["-", "-", "-", "-", "30-Aug-24", "30-Aug-24", "14-Feb-25", "14-Feb-25", "14-Feb-25"],
    "CURRENT HMR": [5110.0, 5208.9, 2602.3, 2622.0, 1920.9, 1959.9, 688.0, 706.7, 688.3],
    "Last Service Date": ["16-Apr-25", "16-Apr-25", "08-Apr-25", "15-Mar-25", "20-Mar-25", "25-Jan-25", "14-Feb-25", "14-Feb-25", "14-Feb-25"],
    "Last Service HMR": [5105.3, 5202.8, 2547.0, 2300.0, 1540.0, 1157.0, 0.0, 0.0, 0.0]
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert date strings to datetime objects
def parse_date(date_str):
    if date_str == "-":
        return None
    try:
        return datetime.strptime(date_str, "%d-%b-%y")
    except:
        return datetime.strptime(date_str, "%d-%b-%Y")

df['Commissioning Date'] = df['Commissioning Date'].apply(parse_date)
df['Last Service Date'] = df['Last Service Date'].apply(lambda x: datetime.strptime(x, "%d-%b-%y"))

# Streamlit app
st.title("Vehicle Service Schedule Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_asset = st.sidebar.selectbox("Select Asset", ["All"] + list(df["Asst.No"].unique()))
show_overdue = st.sidebar.checkbox("Show Only Overdue Services", value=False)

# Filter data
if selected_asset != "All":
    df = df[df["Asst.No"] == selected_asset]

# Calculate service intervals
def calculate_next_service(last_service_hmr, current_hmr, interval):
    return last_service_hmr + interval

# Main display
st.header("Service Schedule Overview")

# Display basic info
st.subheader("Asset Information")
st.dataframe(df[["Asst.No", "Equipment", "M/c Sr.No", "Commissioning Date", "CURRENT HMR", "Last Service Date", "Last Service HMR"]])

# Service intervals
intervals = {
    "Engine Oil Filter": 1000,
    "Fuel Filter": 1000,
    "Bypass Filter": 1000,
    "Racor Fuel Filter": 1000,
    "Fuel Tank Ventilation Filter": 1000,
    "Air Filter Primary": 1500,
    "Air Filter Secondary": 4500,
    "APM Filter": 3000,
    "Climate Unit Filter": 2000,
    "Gear Box Filter": 5000,
    "Power Steering Filter": 5000,
    "Breather Element Filter": 60,  # days
    "Return Line Filter": 120,  # days
    "Engine Oil Change": 1000,
    "Rear Axle Oil": 5000,
    "Transmission Oil": 5000,
    "Power Steering Oil": 5000,
    "Coolant": 4000,
    "Hydraulic Oil": 365  # days
}

# Calculate and display next service dates
st.subheader("Next Service Due Dates")
service_data = []

for asset in df.to_dict('records'):
    for service, interval in intervals.items():
        if "days" in service.lower() or service in ["Breather Element Filter", "Return Line Filter", "Hydraulic Oil"]:
            # Time-based services
            next_service_date = asset["Last Service Date"] + timedelta(days=interval)
            days_left = (next_service_date - datetime.now()).days
            status = "Overdue" if days_left < 0 else "Due Soon" if days_left < 30 else "OK"
            
            if show_overdue and status != "Overdue":
                continue
                
            service_data.append({
                "Asset": asset["Asst.No"],
                "Service": service,
                "Last Service": asset["Last Service Date"].strftime("%d-%b-%Y"),
                "Interval": f"{interval} days",
                "Next Service Due": next_service_date.strftime("%d-%b-%Y"),
                "Days Left": days_left,
                "Status": status
            })
        else:
            # HMR-based services
            next_service_hmr = asset["Last Service HMR"] + interval
            hmr_left = next_service_hmr - asset["CURRENT HMR"]
            status = "Overdue" if hmr_left < 0 else "Due Soon" if hmr_left < 200 else "OK"
            
            if show_overdue and status != "Overdue":
                continue
                
            service_data.append({
                "Asset": asset["Asst.No"],
                "Service": service,
                "Last Service": f"{asset['Last Service HMR']} HMR",
                "Interval": f"{interval} HMR",
                "Next Service Due": f"{next_service_hmr} HMR",
                "HMR Left": hmr_left,
                "Status": status
            })

service_df = pd.DataFrame(service_data)

# Color coding for status
def color_status(val):
    color = 'red' if val == "Overdue" else 'orange' if val == "Due Soon" else 'green'
    return f'color: {color}'

styled_df = service_df.style.applymap(color_status, subset=['Status'])

st.dataframe(styled_df)

# Overdue services summary
overdue = service_df[service_df["Status"] == "Overdue"]
if not overdue.empty:
    st.subheader("⚠️ Overdue Services")
    st.dataframe(overdue)
else:
    st.success("No overdue services!")

# Upcoming services
due_soon = service_df[service_df["Status"] == "Due Soon"]
if not due_soon.empty:
    st.subheader("🔜 Upcoming Services")
    st.dataframe(due_soon)

# Detailed view for selected asset
if selected_asset != "All":
    st.subheader(f"Detailed Service History for {selected_asset}")
    asset_data = df[df["Asst.No"] == selected_asset].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current HMR", asset_data["CURRENT HMR"])
    with col2:
        st.metric("Last Service HMR", asset_data["Last Service HMR"])
    
    st.write(f"Last Service Date: {asset_data['Last Service Date'].strftime('%d-%b-%Y')}")
    
    # Filter services for this asset
    asset_services = service_df[service_df["Asset"] == selected_asset]
    st.dataframe(asset_services)
