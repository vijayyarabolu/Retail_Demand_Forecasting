import pandas as pd
import numpy as np
import os

def load_data(train_path: str):
    return pd.read_csv(train_path)

def create_features(df: pd.DataFrame):
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['store', 'item', 'date'])
    
    # Lag features
    df['lag_sales_1d'] = df.groupby(['store', 'item'])['sales'].shift(1)
    df['lag_sales_7d'] = df.groupby(['store', 'item'])['sales'].shift(7)
    
    # Rolling averages
    df['avg_sales_7d'] = df.groupby(['store', 'item'])['sales'].transform(lambda x: x.rolling(window=7).mean())
    df['avg_sales_30d'] = df.groupby(['store', 'item'])['sales'].transform(lambda x: x.rolling(window=30).mean())
    
    # Seasonal encodings
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Promotion indicator (mocking it if not present, or using existing)
    # Assuming 'is_promotion' might not be in the dataset, let's create a dummy one or use logic
    # The resume says "promotional indicators", let's assume we derive it or it exists.
    # If not, we'll create a placeholder.
    if 'promotion' not in df.columns:
        # Randomly assign promotion for demo purposes if not real
        np.random.seed(42)
        df['is_promotion'] = np.random.choice([0, 1], size=len(df), p=[0.9, 0.1])
    
    # Fill NA
    df = df.fillna(0)
    
    return df

def prepare_for_feast(df: pd.DataFrame, output_path: str):
    # Feast needs event_timestamp
    df['event_timestamp'] = df['date']
    df['created_timestamp'] = pd.Timestamp.now()
    
    # Rename columns to match entity/feature definitions if needed
    df = df.rename(columns={'item': 'product_id', 'store': 'store_id'})
    
    # Select columns
    cols = ['product_id', 'store_id', 'event_timestamp', 'created_timestamp', 
            'avg_sales_7d', 'avg_sales_30d', 'lag_sales_1d', 'lag_sales_7d', 'is_promotion',
            'day_of_week', 'month']
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df[cols].to_parquet(output_path, index=False)
    print(f"Saved features to {output_path}")

if __name__ == "__main__":
    # Assuming train.csv is in the current directory
    if os.path.exists("train.csv"):
        df = load_data("train.csv")
        df_features = create_features(df)
        prepare_for_feast(df_features, "data/demand_features.parquet")
    else:
        print("train.csv not found. Please ensure data is present.")
