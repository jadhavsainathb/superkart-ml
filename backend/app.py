import joblib
import pandas as pd
import psycopg2
import json
import time

from datetime import datetime
from flask import Flask, request, jsonify


superKart_predictor_api = Flask(
    "SuperKart Product Sales Predictor"
)

# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------
model = joblib.load(
    "model/superKart_model_v1_0.joblib"
)

# ---------------------------------------------------------
# RDS connection
# ---------------------------------------------------------
DB_HOST = "superkartdb.c5ywy8ocsual.ap-south-1.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "postgres"

DB_USER = "postgres"
DB_PASSWORD = "postgres"


def get_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def log_prediction(
    request_time,
    response_time,
    duration_ms,
    input_parameters,
    prediction_output
):

    conn = get_connection()

    cur = conn.cursor()

    insert_query = """
    INSERT INTO prediction_logs (

        request_time,
        response_time,
        duration_ms,
        input_parameters,
        prediction_output,
        model_version

    )

    VALUES (

        %s,
        %s,
        %s,
        %s,
        %s,
        %s

    )
    """

    cur.execute(

        insert_query,

        (

            request_time,
            response_time,
            duration_ms,

            json.dumps(
                input_parameters
            ),

            json.dumps(
                prediction_output
            ),

            "v1"

        )

    )

    conn.commit()

    cur.close()
    conn.close()


@superKart_predictor_api.get("/")
def home():

    return (
        "Welcome to the SuperKart "
        "Product Sales Prediction API!"
    )


@superKart_predictor_api.post(
    "/v1/predict"
)
def predict_sales():

    request_time = datetime.now()

    start = time.time()

    data = request.get_json()

    sample = {

        "Product_Weight":
        data["Product_Weight"],

        "Product_Allocated_Area":
        data["Product_Allocated_Area"],

        "Product_Sugar_Content":
        data["Product_Sugar_Content"],

        "Product_Type":
        data["Product_Type"],

        "Product_MRP":
        data["Product_MRP"],

        "Store_Id":
        data["Store_Id"],

        "Store_Establishment_Year":
        data[
            "Store_Establishment_Year"
        ],

        "Store_Size":
        data["Store_Size"],

        "Store_Location_City_Type":
        data[
            "Store_Location_City_Type"
        ],

        "Store_Type":
        data["Store_Type"]

    }

    input_df = pd.DataFrame(
        [sample]
    )

    prediction = model.predict(
        input_df
    )[0]

    result = {

        "Predicted_Product_Store_Sales_Total":
        round(
            float(prediction),
            2
        )

    }

    response_time = datetime.now()

    duration_ms = int(
        (
            time.time() - start
        ) * 1000
    )

    log_prediction(

        request_time,
        response_time,
        duration_ms,

        sample,

        result

    )

    return jsonify(result)


if __name__ == "__main__":

    superKart_predictor_api.run(

        host="0.0.0.0",

        port=7860,

        debug=True

    )