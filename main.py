import time
import streamlit as st
import pandas as pd
import pyodbc

# Database connection details
server = 'xintel-events-db-server.database.windows.net'
database = 'xintel_events_db'
username = 'xintel_admin'
password = 'Momentum@2025'
driver = '{ODBC Driver 18 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
connection = pyodbc.connect(connection_string)
print("Connection established successfully.")

# Function to establish connection
def get_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to fetch data
def fetch_data(query):
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
            return None
    return None

# Streamlit UI
st.set_page_config(page_title="Real Estate CP Meet", layout="wide")
st.title(" Raheja CP Meet")
st.markdown("---")

# Custom CSS for UI enhancement
st.markdown("""
    <style>
        .main {background-color: #f0f2f6; padding-top: 0px !important;}
        
        
       
        
        .stButton>button {
            background-color: #115DBF;
            color: white;
            padding: 8px 8px;
            border-radius: 10px;
            font-size: 10px;
            border: none;
            margin-right: 20px !important; /* Reduce space between buttons */
        }
        .stButton>button:hover {
            background-color: #003F88;
            color:white;
            cursor: pointer;
        }
       .stButton>button:active, .stButton>button:focus {
            color: white !important;  /* Dark blue text */
            outline: none !important;
        }
        .stButton>button:focus-visible {
            color: white !important;  /* Ensures no red text */
        }
        .metric-box {
            background-color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)


# Fetch and display total PAX
pax_query = "SELECT SUM(actual_guest_count) AS total_pax FROM [dbo].[attendance_details]"
unique_query = "SELECT COUNT(actual_guest_count) AS unique_pax FROM [dbo].[attendance_details] WHERE actual_guest_count >= 0"
cp_base_query = "SELECT COUNT(xr_code) AS xr_code FROM [dbo].[attendance_details]"

# Fetch data
pax_data = fetch_data(pax_query)
unique_data = fetch_data(unique_query)
cp_base_data = fetch_data(cp_base_query)

# Extract values safely
total_pax = pax_data["total_pax"].iloc[0] if pax_data is not None and not pax_data.empty else 0
unique_pax = unique_data["unique_pax"].iloc[0] if unique_data is not None and not unique_data.empty else 0
xr_code_count = cp_base_data["xr_code"].iloc[0] if cp_base_data is not None and not cp_base_data.empty else 0

# Display metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<div class='metric-box'><h3>Unique Attendees</h3><h1>{unique_pax}</h1></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><h3>Total PAX</h3><h1>{total_pax}</h1></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-box'><h3>CP BASE</h3><h1>{xr_code_count}</h1></div>", unsafe_allow_html=True)

st.markdown("---")


# Buttons to view tables
col1, col2 = st.columns(2)

if "selected_table" not in st.session_state:
    st.session_state["selected_table"] = None

with col1:
    if st.button("CP Bucket Detail"):
        st.session_state["selected_table"] = "dbo.vw_CP_Bucket_Base_Attendance"

with col2:
    if st.button("SM Detail"):
        st.session_state["selected_table"] = "dbo.vw_SM_Base_Attendance"


# Display selected table
if st.session_state["selected_table"]:
    table_name = st.session_state["selected_table"]
    df = fetch_data(f"SELECT * FROM {table_name} where event_id=2")
    
    if df is not None and not df.empty:
        
        st.dataframe(df, use_container_width=True)
    else:
        st.warning(f"No data available for {table_name}")

# Auto-refresh every 15 seconds
