from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int64, String

# Define entities
product = Entity(name="product_id", value_type=ValueType.STRING, description="Product ID")
store = Entity(name="store_id", value_type=ValueType.STRING, description="Store ID")

# Define the source of the features (offline)
# Assuming we have a parquet file or similar. For now pointing to a csv or parquet.
# In a real scenario, this would be a data warehouse source.
demand_stats_source = FileSource(
    name="demand_stats_source",
    path="/Users/vijay/Desktop/Data Projects/New Resume Projects/Retail_Demand_Forecasting/data/demand_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Define a Feature View
demand_features_view = FeatureView(
    name="demand_features",
    entities=[product, store],
    ttl=timedelta(days=1),
    schema=[
        Field(name="avg_sales_7d", dtype=Float32),
        Field(name="avg_sales_30d", dtype=Float32),
        Field(name="lag_sales_1d", dtype=Float32),
        Field(name="lag_sales_7d", dtype=Float32),
        Field(name="is_promotion", dtype=Int64),
    ],
    online=True,
    source=demand_stats_source,
    tags={"team": "retail_forecasting"},
)
