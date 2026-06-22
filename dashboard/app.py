import pandas as pd
import os, joblib, sys
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

import scrape_flights

MODEL_CONFIGS = {
    "May Logistic Regression": {
        "model_path": "models/may_logistic_regression_model.joblib",
        "preprocessor_path": "models/may_preprocessor.joblib",
        "threshold": 0.40
    },

    "January Logistic Regression": {
        "model_path": "models/jan_logistic_regression_model.joblib",
        "preprocessor_path": "models/jan_preprocessor.joblib",
        "threshold": 0.30
    }
}

headers = ["airline","flight_code","source_city","source_airport",
               "departure_time","stops","duration","destination_city",
               "destination_airport","arrival_time","class","itinerary_type",
               "currency","total_cost","day_searched","timestamp_searched",
               "departure_date","return_date"
]

predictors = [
    "airline",
    "departure_time",
    "stops",
    "duration",
    "total_cost",
    "day_searched",
    "month_searched",
    "days_until_departure"
]

# Load the latest flight data
def load_latest_flight_data():
    df = pd.read_csv("runtime/flight_data.txt",
                     delimiter=",",
                     names=headers
    )
    # Save the latsest flight data to a separate file for quick access and append it to the historical data file
    df.to_csv("data/historical_flights.csv", mode="a", header=False, index=None)
    df.to_csv("data/latest_flights.csv", mode="w+", index=None)

    return df


# Process the data as needed for the model
def process_data(df):
    # Convert timestamps to datetime and calculate days until departure to store in a new column
    df["timestamp_searched"] = pd.to_datetime(df["timestamp_searched"], format="%Y/%m/%d")
    df["departure_date"] = pd.to_datetime(df["departure_date"], format="%Y-%m-%d")
    df["days_until_departure"] = (df["departure_date"] - df["timestamp_searched"]).dt.days

    # Extract the month from the timestamp to create a new feature for seasonality
    df["month_searched"] = df["timestamp_searched"].dt.month

    # Create a unique flight identifier by combining the airline and flight number to capture any flight-specific patterns in the data
    df["flight_id"] = (
        df["airline"].astype(str) + "_" + df["flight_code"].astype(str)
    )

    return df


def make_predictions(df, config):
    # Load the model and preprocessor
    model = joblib.load(config["model_path"])
    preprocessor = joblib.load(config["preprocessor_path"])
    probability_threshold = config["threshold"]

    processed_df = process_data(df)

    X_latest = processed_df[predictors]
    X_processed = preprocessor.transform(X_latest)

    buy_probabilities = model.predict_proba(X_processed)[:, 1]
    predictions = (buy_probabilities >= probability_threshold).astype(int)

    # Keep display copy before selecting predictors
    results_df = processed_df.copy()
    # Add predictions to the results dataframe
    results_df["buy_probability"] = buy_probabilities
    results_df["prediction"] = predictions
    results_df["recommendation"] = results_df["prediction"].map({
        1: "BUY",
        0: "WAIT"
    })

    # Save predictions and probabilities to a new CSV file for review
    results_df.to_csv("data/historical_predictions.csv", mode="a", header=False, index=False)

    return results_df


def dashboard():
    st.set_page_config(
        page_title="Flight Booking Prediction Dashboard",
        page_icon="✈️",
        layout="wide"
    )
    
    st.title("Flight Booking Prediction Dashboard")
    st.caption("Displays the latest flight data along with the model's predictions and probabilities for whether to BUY or WAIT.")

    with st.sidebar:
        st.header("Model Settings")
        st.write("Model: Logistic Regression")
        selected_model = st.selectbox(
            "Select Prediction Model",
            [
                "January Logistic Regression",
                "May Logistic Regression"
            ]
        )

        today = date.today()
        one_year_from_today = date(today.year + 1, today.month, today.day)

        st.write("Departure Date")
        departure_date = st.date_input("Select Departure Date",
                                       value=today,
                                       min_value=today,
                                       max_value=one_year_from_today,
                                       format="YYYY-MM-DD"
        )

        st.write("Return Date")
        return_date = st.date_input("Select Return Date",
                                    value=departure_date,
                                    min_value=departure_date,
                                    max_value=one_year_from_today,
                                    format="YYYY-MM-DD"
        )
        

        st.write(f"Probability Threshold: `{MODEL_CONFIGS[selected_model]['threshold']}`")
        st.write("Target: BUY if curent price is within 5% of future 14-day minimum price, otherwise WAIT")

        run_button = st.button("Load Latest Flights")

    if run_button:
        config = MODEL_CONFIGS[selected_model]
        probability_threshold = config["threshold"]

        # Run the flight scraping function to get the latest flight data and save it to a file
        with st.spinner("Running flight scraper and model predictions..."):
            scrape_flights.main(departure_date=str(departure_date), return_date=str(return_date))

            raw_df = load_latest_flight_data()
            results_df = make_predictions(raw_df, config)

        st.success("Latest flight predictions generated.")

        tab1, tab2 = st.tabs(["Predictions", "Latest Flight Data"])

        with tab1:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Flights Analyzed", len(results_df))
            col2.metric("BUY Recommendations", (results_df["recommendation"] == "BUY").sum())
            col3.metric("WAIT Recommendations", (results_df["recommendation"] == "WAIT").sum())
            col4.metric("Average Price", f"${results_df['total_cost'].mean():.2f}")

            st.subheader("Flight Recommendations")

            display_cols = [
                "airline",
                "flight_code",
                "departure_time",
                "stops",
                "duration",
                "total_cost",
                "days_until_departure",
                "buy_probability",
                "recommendation"
            ]

            st.dataframe(
                results_df[display_cols].sort_values(by="buy_probability", ascending=False).reset_index(drop=True),
                width="stretch"
            )

            st.subheader("BUY Probability by Flight")

            fig, ax = plt.subplots(figsize=(10, 5))

            labels = results_df["flight_id"]

            ax.bar(labels, results_df["buy_probability"], color=results_df["recommendation"].map({
                "BUY": "green",
                "WAIT": "red"
            }))
            ax.axhline(probability_threshold, linestyle="--", color="blue", label=f"Threshold ({probability_threshold})")

            ax.set_xlabel("Flight")
            ax.set_ylabel("BUY Probability")
            ax.set_title("BUY Probability by Flight")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            st.pyplot(fig)

            st.subheader("Price vs BUY Probability")

            fig2, ax2, = plt.subplots(figsize=(8, 5))

            ax2.scatter(
                results_df["total_cost"],
                results_df["buy_probability"],
            )

            ax2.axhline(probability_threshold, linestyle="--", color="blue", label=f"Threshold ({probability_threshold})")
            ax2.set_xlabel("Total Cost")
            ax2.set_ylabel("BUY Probability")
            ax2.set_title("Price vs BUY Probability")
            ax2.legend()
            st.pyplot(fig2)

        with tab2:
            st.subheader("Latest Flight Data")
            st.dataframe(raw_df, width="stretch")

    else:
        st.info("Click 'Load Latest Flights' to generate predictions.")


if __name__ == "__main__":
    dashboard()