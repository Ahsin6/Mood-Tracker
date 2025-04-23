import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv
import time
import warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Mood Tracker",
    page_icon="😊",
    layout="centered"
)

# Define moods with emojis
MOODS = {
    "😊 Happy": "happy",
    "😠 Frustrated": "frustrated",
    "😕 Confused": "confused",
    "🎉 Excited": "excited",
    "😔 Sad": "sad",
    "😐 Neutral": "neutral"
}

def get_google_sheets_client():
    """Initialize and return Google Sheets client"""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Get credentials from environment variable
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        st.error("Google credentials not found!")
        return None
    
    try:
        creds = Credentials.from_service_account_info(
            eval(creds_json),
            scopes=scopes
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to authenticate with Google: {str(e)}")
        return None

def get_or_create_sheet():
    """Get or create the mood tracking sheet"""
    client = get_google_sheets_client()
    if not client:
        return None
    
    try:
        # Try to open existing sheet
        sheet = client.open("Mood Tracker")
    except gspread.SpreadsheetNotFound:
        try:
            # Create new sheet if it doesn't exist
            sheet = client.create("Mood Tracker")
            # Share with anyone with the link with write access
            sheet.share(None, perm_type='anyone', role='writer')
            
            # Initialize the sheet with headers
            worksheet = sheet.sheet1
            worksheet.append_row(["Timestamp", "Mood", "Note"])
            
            # Display the sheet URL
            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.id}"
            st.success(f"Created new Mood Tracker spreadsheet! Access it here: {sheet_url}")
        except Exception as e:
            st.error(f"Failed to create spreadsheet: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error accessing Google Sheets: {str(e)}")
        return None
    
    return sheet.sheet1, sheet.id

def log_mood(mood, note=""):
    """Log a mood entry to Google Sheets"""
    worksheet, sheet_id = get_or_create_sheet()
    if not worksheet:
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([timestamp, mood, note])
        return True
    except Exception as e:
        st.error(f"Failed to log mood: {str(e)}")
        return False

def get_all_moods():
    """Get all mood entries"""
    worksheet, sheet_id = get_or_create_sheet()
    if not worksheet:
        return pd.DataFrame(), None
    
    try:
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            return df, sheet_id
        
        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Date'] = df['Timestamp'].dt.date
        
        return df, sheet_id
    except Exception as e:
        st.error(f"Error reading mood data: {str(e)}")
        return pd.DataFrame(), sheet_id

# Main app
st.title("🎭 Mood Tracker")
st.markdown("Track the emotional pulse of your support tickets throughout the day.")

# Get all mood data
df, sheet_id = get_all_moods()

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    # Show Google Sheet link
    if sheet_id:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        st.markdown(f"[📊 View Google Sheet]({sheet_url})")
    
    # Date selection
    if not df.empty:
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        selected_date = st.date_input(
            "Select Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    else:
        selected_date = st.date_input(
            "Select Date",
            value=datetime.now().date()
        )
    
    # Mood logging section
    st.header("Log a Mood")
    
    selected_mood = st.radio(
        "How are you feeling?",
        list(MOODS.keys()),
        horizontal=True
    )
    
    note = st.text_area("Add a note (optional)", height=100)
    
    if st.button("Submit Mood"):
        if log_mood(MOODS[selected_mood], note):
            st.success("Mood logged successfully!")
            # Force immediate refresh
            st.rerun()
        else:
            st.error("Failed to log mood. Please check your Google Sheets configuration.")

# Main content area
st.header(f"Mood Distribution for {selected_date.strftime('%B %d, %Y')}")

# Filter data for selected date
if not df.empty:
    filtered_df = df[df['Date'] == selected_date]
    
    if filtered_df.empty:
        st.info(f"No moods logged for {selected_date.strftime('%B %d, %Y')}")
    else:
        # Create bar chart
        fig = px.bar(
            filtered_df['Mood'].value_counts().reset_index(),
            x='Mood',
            y='count',
            title=f"Mood Distribution for {selected_date.strftime('%B %d, %Y')}",
            labels={'Mood': 'Mood', 'count': 'Count'},
            color='Mood',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show recent entries
        st.subheader("Recent Entries")
        st.dataframe(
            filtered_df.sort_values('Timestamp', ascending=False)
            .head(5)
            .style.format({'Timestamp': lambda x: x.strftime("%H:%M")})
        )
else:
    st.info("No moods logged yet. Start tracking by submitting a mood in the sidebar!")

# Add a refresh indicator
st.markdown(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
st.markdown("Refreshing every 30 seconds...")

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun() 