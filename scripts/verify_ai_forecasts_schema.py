#!/usr/bin/env python3
"""
Verify ai_forecasts table schema and data integrity
"""

import asyncio
import asyncpg
from datetime import datetime
from app.core.config import settings


async def verify_schema():
    """Verify the ai_forecasts table schema"""
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_forecasts'
            )
        """)
        
        if not table_exists:
            print("❌ Table 'ai_forecasts' does not exist!")
            return False
        
        print("✅ Table 'ai_forecasts' exists")
        
        # Get column information
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'ai_forecasts'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Table Schema:")
        print("-" * 80)
        
        expected_columns = {
            'id': 'integer',
            'forecast_type': 'character varying',
            'forecast_data': 'jsonb',
            'days_ahead': 'integer',
            'generated_at': 'timestamp without time zone',
            'valid_until': 'timestamp without time zone',
            'model_info': 'jsonb',
            'created_at': 'timestamp without time zone'
        }
        
        schema_valid = True
        for col in columns:
            col_name = col['column_name']
            col_type = col['data_type']
            nullable = col['is_nullable']
            default = col['column_default']
            
            expected_type = expected_columns.get(col_name)
            type_match = "✅" if expected_type and expected_type in col_type else "⚠️"
            
            print(f"{type_match} {col_name:20} | {col_type:30} | NULL: {nullable:5} | DEFAULT: {default}")
            
            if expected_type and expected_type not in col_type:
                schema_valid = False
        
        print("-" * 80)
        
        # Check data
        count = await conn.fetchval("SELECT COUNT(*) FROM ai_forecasts")
        print(f"\n📊 Data Count: {count} records")
        
        if count > 0:
            # Get latest records
            latest = await conn.fetch("""
                SELECT 
                    id,
                    forecast_type,
                    days_ahead,
                    generated_at,
                    valid_until,
                    model_info,
                    created_at,
                    jsonb_object_keys(forecast_data) as forecast_keys
                FROM ai_forecasts
                ORDER BY generated_at DESC
                LIMIT 5
            """)
            
            print("\n📈 Latest Records:")
            print("-" * 80)
            for record in latest:
                print(f"ID: {record['id']}")
                print(f"  Type: {record['forecast_type']}")
                print(f"  Days Ahead: {record['days_ahead']}")
                print(f"  Generated: {record['generated_at']}")
                print(f"  Valid Until: {record['valid_until']}")
                print(f"  Model Info: {record['model_info']}")
                print(f"  Created: {record['created_at']}")
                print(f"  Forecast Keys: {record['forecast_keys']}")
                print()
        
        # Verify all required columns are present
        actual_columns = {col['column_name'] for col in columns}
        required_columns = set(expected_columns.keys())
        
        if required_columns == actual_columns:
            print("✅ All required columns present")
        else:
            missing = required_columns - actual_columns
            extra = actual_columns - required_columns
            if missing:
                print(f"❌ Missing columns: {missing}")
                schema_valid = False
            if extra:
                print(f"⚠️  Extra columns: {extra}")
        
        return schema_valid
    
    finally:
        await conn.close()


if __name__ == "__main__":
    result = asyncio.run(verify_schema())
    exit(0 if result else 1)
