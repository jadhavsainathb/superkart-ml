
# Import required libraries
import joblib                       # For loading the trained ML model
import pandas as pd                 # For handling input data
from flask import Flask, request, jsonify   # Flask framework for building API

# -------------------------------------------------------------
# Initialize the Flask application
# -------------------------------------------------------------
# The name helps identify the API service
superKart_predictor_api = Flask("SuperKart Product Sales Predictor")

# -------------------------------------------------------------
# Load the trained machine learning pipeline model
# -------------------------------------------------------------
# This model includes preprocessing steps and the trained algorithm
model = joblib.load("model/superKart_model_v1_0.joblib")


# -------------------------------------------------------------
# Home endpoint
# -------------------------------------------------------------
# Used to verify that the API service is running successfully
@superKart_predictor_api.get('/')
def home():
    return "Welcome to the SuperKart Product Sales Prediction API!"


# -------------------------------------------------------------
# Endpoint for predicting sales of a single product
# -------------------------------------------------------------
# This endpoint expects JSON input containing product and store features
@superKart_predictor_api.post('/v1/predict')
def predict_sales():

    # Read JSON data sent in the API request
    data = request.get_json()

    # Extract the required features from the request
    # These must match the features used during model training
    sample = {
        "Product_Weight": data["Product_Weight"],
        "Product_Allocated_Area": data["Product_Allocated_Area"],
        "Product_Sugar_Content": data["Product_Sugar_Content"],
        "Product_Type": data["Product_Type"],
        "Product_MRP": data["Product_MRP"],
        "Store_Id": data["Store_Id"],
        "Store_Establishment_Year": data["Store_Establishment_Year"],
        "Store_Size": data["Store_Size"],
        "Store_Location_City_Type": data["Store_Location_City_Type"],
        "Store_Type": data["Store_Type"]
    }

    # Convert the input dictionary into a Pandas DataFrame
    # The model expects tabular input format
    input_df = pd.DataFrame([sample])

    # Generate prediction using the trained model pipeline
    prediction = model.predict(input_df)[0]

    # Return prediction as a JSON response
    return jsonify({
        "Predicted_Product_Store_Sales_Total": round(float(prediction),2)
    })


# -------------------------------------------------------------
# Endpoint for batch prediction
# -------------------------------------------------------------
# This endpoint accepts a CSV file containing multiple records
# and returns predictions for each record
@superKart_predictor_api.post('/v1/predictbatch')
def predict_sales_batch():

    # Get uploaded CSV file from request
    file = request.files['file']

    # Convert CSV file into Pandas DataFrame
    input_data = pd.read_csv(file)

    # Generate predictions for all rows
    predictions = model.predict(input_data)

    # Add predictions to the original dataset
    input_data["Predicted_Product_Store_Sales_Total"] = predictions

    # Return predictions as JSON output
    return input_data.to_json(orient="records")


# -------------------------------------------------------------
# Run the Flask application
# -------------------------------------------------------------
# host='0.0.0.0' allows the API to be accessed externally
# port=7860 is commonly used for ML deployment environments
# debug=True enables debugging during development
if __name__ == '__main__':
    superKart_predictor_api.run(host='0.0.0.0', port=7860, debug=True)
