from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix, roc_curve
import matplotlib.pyplot as plt

# Process the May dataset to create a target variable for a supervised learning model that predicts whether to buy now or wait for a better price in the future
def create_target_variable(df, future_window=14, threshold=0.05):
    # future_window: Number of future days to inspect
    # threshold: Threshold for what counts as "close enough" to the future minimum

    # Create a copy of the dataframe to avoid modifying the original
    new_df = df.copy()

    # Sort chronologically within each flight sequence
    new_df = new_df.sort_values(
        by=["flight_id", "timestamp_searched"]
    ).reset_index(drop=True)


    # Find the minimum future price within the next N observations
    new_df["future_min_price"] = (
        new_df.groupby("flight_id")["total_cost"]
        .transform(
            lambda x: x[::-1]
            .rolling(window=future_window, min_periods=1)
            .min()[::-1]
            .shift(-1)
        )
    )

    # Create BUY(1) / WAIT(0) target
    new_df["target"] = (
        new_df["total_cost"] <= new_df["future_min_price"] * (1 + threshold)
        ).astype(int)

    # Drop rows where no future information exists
    new_df = new_df.dropna(subset=["future_min_price"])

    # Inspect class balance
    print(new_df["target"].value_counts())
    print(new_df["target"].value_counts(normalize=True))

    return new_df


# Split the data into training and testing sets
def split_data_chronologically(df, predictors, target, timestamp_col="timestamp_searched", train_size=0.70, val_size=0.15, purge_days=14):
    # Make sure the dataframe is sorted chronologically
    model_df = df[predictors + [target, timestamp_col]].copy()
    model_df = model_df.sort_values(timestamp_col).reset_index(drop=True)

    # Define split sizes
    n = len(model_df)

    train_end_idx = int(n * train_size)
    val_end_idx = int(n * (train_size + val_size))

    train_boundary_date = model_df.loc[train_end_idx, timestamp_col]
    val_boundary_date = model_df.loc[val_end_idx, timestamp_col]

    purge_gap = pd.Timedelta(days=purge_days)

    # Purge rows before validation and test boundaries to prevent data leakage
    train_df = model_df[
        model_df[timestamp_col] < (train_boundary_date - purge_gap)
    ]

    val_df = model_df[
        (model_df[timestamp_col] >= train_boundary_date) &
        (model_df[timestamp_col] < (val_boundary_date - purge_gap))
    ]

    test_df = model_df[
        model_df[timestamp_col] >= val_boundary_date
    ]

    # Separate predictors and target
    X_train = train_df[predictors]
    y_train = train_df[target]

    X_val = val_df[predictors]
    y_val = val_df[target]

    X_test = test_df[predictors]
    y_test = test_df[target]

    return X_train, y_train, X_val, y_val, X_test, y_test, train_df, val_df, test_df



# Function to inspect the splits for date ranges and class balance
def inspect_splits(train_df, val_df, test_df, y_train, y_val, y_test):   
    # verify date ranges
    print("Train:", train_df["timestamp_searched"].min(), "to", train_df["timestamp_searched"].max())
    print("Validation:", val_df["timestamp_searched"].min(), "to", val_df["timestamp_searched"].max())
    print("Test:", test_df["timestamp_searched"].min(), "to", test_df["timestamp_searched"].max())

    # check class balance in each split
    print("\nTrain target balance:")
    print(y_train.value_counts(normalize=True))

    print("\nValidation target balance:")
    print(y_val.value_counts(normalize=True))

    print("\nTest target balance:")
    print(y_test.value_counts(normalize=True))



def create_preprocessor(numerical_features, categorical_features):
    # Preprocessing for logistic regression model
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    return preprocessor


# Function to preprocess the data using the defined preprocessor and return the processed datasets
def preprocess_data(X_train, X_val, X_test, numerical_features, categorical_features):
    preprocessor = create_preprocessor(numerical_features, categorical_features)

    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)
    X_test_processed = preprocessor.transform(X_test)

    return X_train_processed, X_val_processed, X_test_processed, preprocessor


# Evaluate the model on the validation set (NOT TEST SET - ONLY USE THIS FOR FINAL EVALUATION)
def evaluate_model(model, X_train_processed, X_val_processed):
    # Predictions
    y_train_pred = model.predict(X_train_processed)
    y_val_pred = model.predict(X_val_processed)

    # Prediction probabilities
    y_train_prob = model.predict_proba(X_train_processed)[:, 1]
    y_val_prob = model.predict_proba(X_val_processed)[:, 1]

    return y_train_pred, y_val_pred, y_train_prob, y_val_prob


# Print evaluation metrics for each model with different thresholds
def print_evaluation_metrics(y_train, y_val, y_train_pred, y_val_pred, y_val_prob):
    # Accuracy
    print("Training Accuracy:", accuracy_score(y_train, y_train_pred))
    print("Validation Accuracy:", accuracy_score(y_val, y_val_pred))

    # Confusion Matrix
    print("\nValidation Confusion Matrix:")
    print(confusion_matrix(y_val, y_val_pred))

    # Precision, Recall, F1-Score
    print("\nValidation Classification Report:")
    print(classification_report(y_val, y_val_pred))

    # ROC AUC Score
    print("Validation ROC AUC Score:")
    print(roc_auc_score(y_val, y_val_prob))


# Visualize the ROC curve for the validation set of each model with different thresholds
def plot_roc_curve(y_val, y_val_prob, name):
    fpr, tpr, _ = roc_curve(y_val, y_val_prob)

    plt.figure(figsize=(8,6))

    plt.plot(fpr, tpr, label="Validation ROC Curve")
    plt.plot([0,1], [0,1], linestyle="--")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"Validation ROC Curve - {name}")

    plt.legend()
    plt.show()