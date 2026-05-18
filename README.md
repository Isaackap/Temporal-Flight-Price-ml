# Flight Booking Strategy Prediction using Machine Learning

## Overview

This project combines automated flight data collection, machine learning, and an interactive dashboard to analyze airfare pricing behavior and predict potential flight booking opportunities.

The system continuously gathers flight pricing data using the BOOKING.COM API (via RapidAPI), stores and processes the results, trains machine learning models on historical pricing behavior, and serves predictions through a Streamlit dashboard.

The primary goal of the project is to identify whether a flight is likely a good **BUY** opportunity or whether the user should **WAIT** for potentially lower prices in the near future.

The project evolved into a full end-to-end machine learning pipeline involving:
- automated data collection
- feature engineering
- temporal validation
- leakage prevention
- model comparison
- probability threshold tuning
- live prediction deployment

---

# Features

## Flight Data Collection
- Collects live flight pricing data using the BOOKING.COM API via RapidAPI
- Configurable routes, dates, passenger counts, and search settings
- Saves runtime JSON and TXT logs
- Exports structured data to Google Sheets
- Optional email alerts for low-price flights

---

## Machine Learning Pipeline
- Builds a historical airfare pricing dataset over time
- Performs preprocessing and feature engineering
- Engineers BUY/WAIT targets using future rolling price windows
- Trains and evaluates:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Uses chronological train/validation/test splitting
- Implements purge gaps to reduce temporal leakage
- Tunes probability thresholds for deployment decisions

---

## Interactive Dashboard
- Built using Streamlit
- Runs the flight scraper directly from the dashboard
- Displays:
  - latest scraped flights
  - BUY probabilities
  - BUY/WAIT recommendations
  - model statistics and charts
- Allows exploration of raw flight data alongside model predictions

---

# Example Dashboard Workflow

```text
Run Dashboard
    ↓
Collect Latest Flight Data
    ↓
Process and Engineer Features
    ↓
Apply Saved Preprocessor
    ↓
Generate BUY/WAIT Predictions
    ↓
Display Results in Dashboard
```

---

# Machine Learning Target

The project reframes airfare prediction into a classification problem.

A flight is labeled as:

- **BUY**
  - if the current price is within 5% of the minimum future price observed within the next 14 observations
- **WAIT**
  - otherwise

This approach focuses on identifying practical booking opportunities rather than directly predicting exact future prices.

---

# Tech Stack

## Languages & Frameworks
- Python 3.12
- Streamlit
- Jupyter Notebook

---

## Machine Learning Libraries
- scikit-learn
- XGBoost
- pandas
- numpy
- matplotlib

---

## Data Collection & APIs
- requests
- BOOKING.COM API (RapidAPI)

---

## Cloud & External Services
- Google Sheets API
- Gmail SMTP

---

## Environment & Tooling
- uv package manager

---

# Project Structure

```text
FLIGHTMODEL/
│
├── dashboard/                 # Streamlit dashboard
|   └── app.py                     # Main Streamlit application
│
├── data/
│   ├── historical_flights.csv
│   ├── latest_flights.csv
│   └── latest_predictions.csv
│
├── models/
│   ├── logistic_regression_model.joblib
│   ├── preprocessor.joblib
│   ├── random_forest_model.joblib
│   └── xgboost_model.joblib
│
├── notebooks/
│   └── flight_prediction.ipynb
│
├── runtime/
│   ├── flight_alert.txt
│   ├── flight_data.txt
│   └── search_flights_response.json
│
├── scrape_flights.py          # Flight data collection pipeline
├── helper.py                  # Shared preprocessing/helper functions
├── gsheets.py                 # Google Sheets export logic
├── config.py                  # Configurable parameters
├── .env                       # Environment variables
├── pyproject.toml
└── uv.lock
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/Temporal-Flight-Price-ml.git

cd Temporal-Flight-Price-ml
```

---

## Create Environment

```bash
uv venv
```

---

## Install Dependencies

```bash
uv sync
```

or manually:

```bash
uv add pandas numpy scikit-learn xgboost matplotlib streamlit requests python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib joblib
```

---

# Environment Variables

Create a `.env` file in the project root:

```env
RAPIDAPI_KEY=your_rapidapi_key_here

SENDER_EMAIL=your_email@gmail.com
RECEIVER_EMAIL=recipient_email@gmail.com
PASSWORD=your_gmail_app_password

SPREADSHEET_ID=your_google_sheet_id
```

---

# Running the Dashboard

```bash
uv run streamlit run app.py
```

The dashboard will:
1. Collect the latest flight data
2. Process and engineer features
3. Generate predictions using the trained model
4. Display BUY/WAIT recommendations

---

# Model Findings

The project discovered several important machine learning insights:

- Logistic Regression generalized more effectively than Random Forest and XGBoost under temporal validation
- Airfare pricing behavior changes substantially across booking horizons
- Models trained on mid-booking periods struggled to generalize to near-departure pricing regimes
- Temporal distribution shift significantly affected probability calibration and final test performance

These findings highlight the challenges of real-world temporal forecasting systems.

---

# Future Improvements

Potential future enhancements include:

- Collecting data across multiple seasons and years
- Expanding to additional flight routes
- Building booking-horizon-specific models
- Incorporating external economic or holiday features
- Deploying automated retraining pipelines
- Hosting the dashboard publicly
- Exploring LSTM or sequential time-series models

---

# Notes

- Sensitive files such as `.env`, `token.json`, and `credentials.json` should not be committed to source control
- Google Sheets export and email alerts can be disabled independently
- The current model is primarily trained on Houston → Japan flight behavior and may not generalize well to all routes or seasons

---

# Author

Isaac Kapeel
