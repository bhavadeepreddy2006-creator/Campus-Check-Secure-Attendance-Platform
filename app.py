import streamlit as st
import pandas as pd
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# ==========================
# CONFIG
# ==========================

EVENT_LAT = 16.463333
EVENT_LON = 80.404444
ALLOWED_RADIUS = 200
APPROVED_WIFI = "CITY"

DATA_FILE = "attendance.csv"

ADMIN_USERNAME = "bhavadeep reddy"
ADMIN_PASSWORD = "09072224"

# ==========================
# SESSION STATE
# ==========================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================
# SCHEMA
# ==========================

COLUMNS = [
    "Student ID",
    "Student Name",
    "WiFi SSID",
    "Latitude",
    "Longitude",
    "Distance(M)",
    "Verified",
    "Check In",
    "Check Out",
    "Attendance Date"
]

# ==========================
# DB SAFETY
# ==========================

def init_db():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)

def load_data():
    df = pd.read_csv(DATA_FILE, dtype=str)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ==========================
# DISTANCE
# ==========================

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

def get_location():
    return EVENT_LAT, EVENT_LON

# ==========================
# INIT
# ==========================

init_db()

st.set_page_config(page_title="Attendance System", layout="wide")

st.title("🎓 Python Class Attendance System")

# ==========================
# SIDEBAR MENU
# ==========================

menu = st.sidebar.radio(
    "Navigation",
    ["📍 Check-In", "🚪 Check-Out", "📊 Reports", "🔐 Admin Login"]
)

today = datetime.now().strftime("%Y-%m-%d")

# ==========================
# CHECK-IN
# ==========================

if menu == "📍 Check-In":

    st.subheader("Student Check-In")

    student_id = st.text_input("Student ID")
    student_name = st.text_input("Student Name")

    if st.button("Check In"):

        if not student_id or not student_name:
            st.error("All fields required")
            st.stop()

        df = load_data()

        if (df["Student ID"] == student_id).any() and (df["Attendance Date"] == today).any():
            st.warning("Already checked in today")
            st.stop()

        wifi = APPROVED_WIFI
        lat, lon = get_location()
        dist = calculate_distance(EVENT_LAT, EVENT_LON, lat, lon)

        if wifi != APPROVED_WIFI or dist > ALLOWED_RADIUS:
            st.error("Verification Failed (WiFi/GPS)")
            st.stop()

        new_row = {
            "Student ID": student_id,
            "Student Name": student_name,
            "WiFi SSID": wifi,
            "Latitude": lat,
            "Longitude": lon,
            "Distance(M)": round(dist, 2),
            "Verified": "True",
            "Check In": str(datetime.now()),
            "Check Out": "",
            "Attendance Date": today
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)

        st.success("Check-In Successful 🎉")

# ==========================
# CHECK-OUT
# ==========================

elif menu == "🚪 Check-Out":

    st.subheader("Student Check-Out")

    student_id = st.text_input("Student ID")

    if st.button("Check Out"):

        df = load_data()

        record = df[(df["Student ID"] == student_id) & (df["Attendance Date"] == today)]

        if record.empty:
            st.error("No record found")
            st.stop()

        idx = record.index[0]
        df.loc[idx, "Check Out"] = str(datetime.now())
        save_data(df)

        st.success("Check-Out Successful")

# ==========================
# REPORTS (ROLE BASED)
# ==========================

elif menu == "📊 Reports":

    st.subheader("Attendance Reports")

    df = load_data()

    if not st.session_state.admin_logged_in:

        st.info("👤 Student View (Your Records Only)")

        student_id = st.text_input("Enter Your Student ID")

        if student_id:
            user_df = df[df["Student ID"] == student_id]

            if user_df.empty:
                st.warning("No records found")
            else:
                st.dataframe(user_df, use_container_width=True)

    else:
        st.success("🔐 Admin Access")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Download Full Report",
            df.to_csv(index=False),
            "attendance_report.csv",
            "text/csv"
        )

# ==========================
# ADMIN LOGIN (UNDER REPORTS IN SIDEBAR FLOW)
# ==========================

elif menu == "🔐 Admin Login":

    st.subheader("Admin Authentication")

    if not st.session_state.admin_logged_in:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Admin Logged In")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    else:
        st.success("Already Logged In")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()