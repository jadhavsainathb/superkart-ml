
# -----------------------------------------------------
# Import required libraries
# -----------------------------------------------------
import requests
import streamlit as st
import pandas as pd


# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="SuperKart Sales Predictor",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 SuperKart Product Sales Prediction")
st.write("Provide product and store details to estimate expected product sales.")


# -----------------------------------------------------
# Session State for Prediction History
# -----------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------------------------------
# Input Layout (Balanced Columns)
# -----------------------------------------------------
col1, col2 = st.columns(2)


# -----------------------------
# Column 1 Inputs
# -----------------------------
with col1:

    st.markdown("**Product Weight**")
    Product_Weight = st.number_input(
        "Product Weight",
        min_value=0.0,
        value=12.0,
        label_visibility="collapsed"
    )

    st.markdown("**Product Allocated Area (Display Ratio)**")
    Product_Allocated_Area = st.number_input(
        "Product Allocated Area",
        min_value=0.0,
        value=0.05,
        label_visibility="collapsed"
    )

    st.markdown("**Product MRP (USD)**")
    Product_MRP = st.number_input(
        "Product MRP",
        min_value=0.0,
        value=150.0,
        label_visibility="collapsed"
    )

    st.markdown("**Store Establishment Year**")
    Store_Establishment_Year = st.number_input(
        "Store Establishment Year",
        min_value=1950,
        max_value=2025,
        value=2000,
        label_visibility="collapsed"
    )

    st.markdown("**Store Size**")
    Store_Size = st.selectbox(
        "Store Size",
        ["Medium", "High", "Small"],
        label_visibility="collapsed"
    )


# -----------------------------
# Column 2 Inputs
# -----------------------------
with col2:

    st.markdown("**Product Sugar Content**")
    Product_Sugar_Content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"],
        label_visibility="collapsed"
    )

    st.markdown("**Product Type**")
    Product_Type = st.selectbox(
        "Product Type",
        [
            "Frozen Foods","Dairy","Canned","Baking Goods","Health and Hygiene",
            "Snack Foods","Meat","Household","Hard Drinks","Fruits and Vegetables",
            "Breads","Soft Drinks","Breakfast","Others","Starchy Foods","Seafood"
        ],
        label_visibility="collapsed"
    )

    st.markdown("**Store ID**")
    Store_Id = st.selectbox(
        "Store ID",
        ["OUT004","OUT003","OUT001","OUT002"],
        label_visibility="collapsed"
    )

    st.markdown("**Store Location City Type**")
    Store_Location_City_Type = st.selectbox(
        "Store Location City Type",
        ["Tier 2","Tier 1","Tier 3"],
        label_visibility="collapsed"
    )

    st.markdown("**Store Type**")
    Store_Type = st.selectbox(
        "Store Type",
        ["Supermarket Type2","Departmental Store","Supermarket Type1","Food Mart"],
        label_visibility="collapsed"
    )


# -----------------------------------------------------
# Prepare Input Data
# -----------------------------------------------------
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Type": Product_Type,
    "Product_MRP": Product_MRP,
    "Store_Id": Store_Id,
    "Store_Establishment_Year": Store_Establishment_Year,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type
}


# -----------------------------------------------------
# Prediction Button (Left Aligned)
# -----------------------------------------------------
st.write("")
predict_button = st.button("Predict Sales", type="primary")


# -----------------------------------------------------
# Prediction Result
# -----------------------------------------------------
if predict_button:

    response = requests.post(
        "http://backend:7860/v1/predict",
        json=product_data
    )

    if response.status_code == 200:

        result = response.json()
        predicted_sales = result["Predicted_Product_Store_Sales_Total"]

        st.divider()

        # KPI Prediction Card
        st.markdown("## 📊 Predicted Sales")

        st.metric(
            label="Estimated Product Store Sales",
            value=f"${predicted_sales:,.2f}"
        )

        # Input Summary Table
        st.markdown("### Input Summary")

        input_df = pd.DataFrame([product_data])
        st.dataframe(input_df)

        # Save to History
        history_record = product_data.copy()
        history_record["Predicted_Sales"] = predicted_sales
        st.session_state.history.append(history_record)

    else:
        st.error("Error connecting to prediction API")


# -----------------------------------------------------
# Prediction History
# -----------------------------------------------------
if st.session_state.history:

    st.divider()
    st.markdown("### 📜 Prediction History")

    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df)


# -----------------------------------------------------
# Batch Prediction
# -----------------------------------------------------
st.divider()
st.subheader("Batch Prediction")

file = st.file_uploader(
    "Upload CSV file containing product and store data",
    type=["csv"]
)

if file is not None:

    input_df = pd.read_csv(file)

    st.write("### Uploaded Data")
    st.dataframe(input_df)

    if st.button("Predict Batch Sales"):

        response = requests.post(
            "http://backend:7860/v1/predictbatch",
            files={"file": file}
        )

        if response.status_code == 200:

            result = response.json()
            results_df = pd.DataFrame(result)

            st.subheader("Batch Prediction Results")
            st.dataframe(results_df)

            csv = results_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Predictions CSV",
                data=csv,
                file_name="superkart_sales_predictions.csv",
                mime="text/csv"
            )

        else:
            st.error("Batch prediction API error")
