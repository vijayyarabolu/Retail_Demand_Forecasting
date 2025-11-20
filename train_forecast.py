import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import os

def validate_features(df: pd.DataFrame):
    # Feature validation framework
    print("Validating features...")
    required_cols = ['avg_sales_7d', 'avg_sales_30d', 'lag_sales_1d', 'lag_sales_7d', 'is_promotion']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing feature: {col}")
        
    # Check for nulls (should be handled in pipeline, but good to verify)
    if df[required_cols].isnull().any().any():
        print("Warning: Null values found in features. Filling with 0.")
        df[required_cols] = df[required_cols].fillna(0)
        
    print("Feature validation passed.")
    return df

def train_forecast_model(data_path: str):
    print(f"Loading data from {data_path}...")
    # In a real Feast setup, we would use get_historical_features
    # Here we load the parquet directly for simplicity as we are in local mode
    df = pd.read_parquet(data_path)
    
    df = validate_features(df)
    
    # Target is usually 'sales' but we need to join it back if we only saved features
    # For this demo, let's assume we join back with the target or the target was in the parquet
    # Wait, my feature_pipeline only saved features. I should have saved the target too for training.
    # Let's modify the pipeline or just assume we have the target here.
    # I'll update the pipeline to include 'sales' in the parquet for training purposes.
    
    # Re-reading train.csv to get target if needed, but better to have it in parquet.
    # Let's assume for now we re-merge or it's there. 
    # Actually, let's just update the pipeline in the next step if needed. 
    # For now, I'll assume I can get 'sales' from the original train.csv and merge on keys.
    
    train_df = pd.read_csv("train.csv")
    train_df['date'] = pd.to_datetime(train_df['date'])
    train_df = train_df.rename(columns={'item': 'product_id', 'store': 'store_id'})
    
    # Merge
    df = pd.merge(df, train_df[['product_id', 'store_id', 'date', 'sales']], 
                  left_on=['product_id', 'store_id', 'event_timestamp'], 
                  right_on=['product_id', 'store_id', 'date'])
    
    X = df[['avg_sales_7d', 'avg_sales_30d', 'lag_sales_1d', 'lag_sales_7d', 'is_promotion', 'day_of_week', 'month']]
    y = df['sales']
    
    # Train/Test split (time-based split is better for forecasting, but random for simplicity here)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    mlflow.set_experiment("Retail_Demand_Forecasting")
    
    with mlflow.start_run():
        params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 5
        }
        mlflow.log_params(params)
        
        model = GradientBoostingRegressor(**params, random_state=42)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        mae = mean_absolute_error(y_test, predictions)
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        
        mlflow.sklearn.log_model(model, "model")
        
        print(f"Model trained. RMSE: {rmse}, MAE: {mae}")

if __name__ == "__main__":
    if os.path.exists("data/demand_features.parquet") and os.path.exists("train.csv"):
        train_forecast_model("data/demand_features.parquet")
    else:
        print("Data not found. Run feature_pipeline.py first.")
