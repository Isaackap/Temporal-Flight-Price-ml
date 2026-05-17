import pandas as pd
import os, joblib
# import scrape_flights

PROBABILITY_THRESHOLD = 0.40  # Set a threshold for classifying as "BUY" or "WAIT"

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

def process_data(df):
    # Process the data as needed for the model

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

if __name__ == "__main__":
    # Load the latest flight data, append it to the historical data, and save the updated historical data.
    # Also saves the latest data in a separate file for quick access.

    # try:
    #     scrape_flights.main()
    # except Exception as e:
    #     print("Error occurred during flight scraping: ", e)

    headers = ["airline","flight_code","source_city","source_airport",
               "departure_time","stops","duration","destination_city",
               "destination_airport","arrival_time","class","itinerary_type",
               "currency","total_cost","day_searched","timestamp_searched",
               "departure_date","return_date"
    ]

    # Load the latest flight data
    df = pd.read_csv("runtime/flight_data.txt", delimiter=",", names=headers)
    # Save the latsest flight data to a separate file for quick access and append it to the historical data file
    # df.to_csv("data/historical_flights.csv", mode="a", header=False, index=None)
    df.to_csv("data/latest_flights.csv", mode="w+", index=None)

    # Process the data for the model
    processed_df = process_data(df)

    # Keep display copy before selecting predictors
    results_df = processed_df.copy()

    # Select only the predictor columns for the model
    X_latest = processed_df[predictors]

    # Load the Logistic regression model and preprocessor from the 'models' directory
    model = joblib.load(os.path.join("models", "logistic_regression_model.joblib"))
    preprocessor = joblib.load(os.path.join("models", "preprocessor.joblib"))

    # Process the latest flight data using the same preprocessor used for training the model
    X_processed = preprocessor.transform(X_latest)

    buy_probabilities = model.predict_proba(X_processed)[:, 1]  # Get probabilities for the "BUY" class

    # Apply tuned probability threshold to classify as "BUY" or "WAIT"
    predictions = (buy_probabilities >= PROBABILITY_THRESHOLD).astype(int)

    # Add predictions to the results dataframe
    results_df["buy_probability"] = buy_probabilities
    results_df["prediction"] = predictions
    results_df["recommendation"] = results_df["prediction"].map({
        1: "BUY",
        0: "WAIT"
    })

    # Save predictions and probabilities to a new CSV file for review
    results_df.to_csv("data/latest_predictions.csv", mode="w+", index=False)

    print(results_df[[
        "airline",
        "flight_code",
        "departure_time",
        "stops",
        "duration",
        "total_cost",
        "days_until_departure",
        "buy_probability",
        "recommendation"
    ]])

    print(processed_df[[
        "total_cost",
        "days_until_departure",
        "month_searched"
    ]].describe())