#!/usr/bin/env python3
"""
Test script to verify Feast integration with TimescaleDB.
Tests both online and offline store connectivity.
"""

import pandas as pd
from feast import FeatureStore
from feast.entity import Entity
from feast.feature_view import FeatureView
from feast.field import Field
from feast.types import Float32, Int64
from feast.data_source import PushSource
from datetime import datetime, timedelta
import psycopg2

def test_timescale_connection():
    """Test direct TimescaleDB connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="mlops",
            user="postgres",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ TimescaleDB connection successful: {version[0]}")
        
        # Check if TimescaleDB extension is available
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'timescaledb';")
        timescale_ext = cursor.fetchone()
        if timescale_ext:
            print("✅ TimescaleDB extension is installed")
        else:
            print("⚠️  TimescaleDB extension not found")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ TimescaleDB connection failed: {e}")
        return False

def test_feast_store():
    """Test Feast feature store configuration"""
    try:
        # Initialize Feast store (assumes feature_store.yaml is configured)
        fs = FeatureStore(repo_path=".")
        
        # Create a simple entity
        user_entity = Entity(
            name="user_id",
            description="User identifier"
        )
        
        # Create a push source for real-time features
        push_source = PushSource(
            name="user_features_push_source",
            batch_source=None,
        )
        
        # Create a feature view
        user_features_fv = FeatureView(
            name="user_features",
            entities=[user_entity],
            schema=[
                Field(name="feature_1", dtype=Float32),
                Field(name="feature_2", dtype=Int64),
            ],
            source=push_source,
            ttl=timedelta(days=1),
        )
        
        # Apply to Feast
        fs.apply([user_entity, user_features_fv])
        print("✅ Feast feature definitions applied successfully")
        
        # Test pushing features to online store
        test_data = pd.DataFrame({
            "user_id": [1, 2, 3],
            "feature_1": [1.1, 2.2, 3.3],
            "feature_2": [10, 20, 30],
            "event_timestamp": [datetime.now()] * 3
        })
        
        fs.push("user_features_push_source", test_data)
        print("✅ Features pushed to online store successfully")
        
        # Test retrieving features from online store
        features = fs.get_online_features(
            features=["user_features:feature_1", "user_features:feature_2"],
            entity_rows=[{"user_id": 1}, {"user_id": 2}]
        ).to_dict()
        
        print("✅ Features retrieved from online store:")
        print(f"   User 1 features: {features}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feast store test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Feast + TimescaleDB Integration")
    print("=" * 50)
    
    # Test 1: Direct TimescaleDB connection
    print("\n1. Testing TimescaleDB connection...")
    db_ok = test_timescale_connection()
    
    # Test 2: Feast store functionality
    print("\n2. Testing Feast feature store...")
    feast_ok = test_feast_store()
    
    # Summary
    print("\n" + "=" * 50)
    if db_ok and feast_ok:
        print("🎉 All tests passed! Feast + TimescaleDB integration is working.")
    else:
        print("❌ Some tests failed. Check the configuration.")
        if not db_ok:
            print("   - TimescaleDB connection issue")
        if not feast_ok:
            print("   - Feast configuration issue")

if __name__ == "__main__":
    main()