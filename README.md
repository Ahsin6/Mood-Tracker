# Mood Tracker

A simple web application for tracking team moods throughout the day, built with Streamlit and Google Sheets.

## Features

- Real-time mood tracking with emojis
- Optional notes for each mood entry
- Date-based filtering
- Visual mood distribution charts
- Auto-refresh every 30 seconds
- Mobile-friendly interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Sheets API:
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create a service account
   - Download credentials JSON
   - Set environment variable:
```bash
export GOOGLE_CREDENTIALS_JSON='{"type": "service_account", ...}'
```

## Run

```bash
streamlit run app.py
```

Access the app at (https://ahsin6-mood-tracker-app-lyj8sk.streamlit.app/)

## Usage

1. Select a date to view historical data
2. Log moods using emoji buttons
3. Add optional notes
4. View mood distribution charts
5. See recent entries

The app automatically creates a Google Sheet for data storage and provides a link to view it directly. 
