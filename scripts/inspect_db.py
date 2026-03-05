"""
Database Schema Inspector
يفحص قاعدة البيانات ويعرض الجداول والأعمدة والعلاقات
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def inspect_database():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    print("=" * 80)
    print("DATABASE SCHEMA INSPECTION")
    print("=" * 80)
    
    # ========================================================================
    # Get all tables
    # ========================================================================
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    print(f"\n📊 TABLES ({len(tables)}):")
    print("-" * 80)
    for t in tables:
        print(f"  • {t['table_name']}")
    
    # ========================================================================
    # Get all views
    # ========================================================================
    views = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    print(f"\n👁️  VIEWS ({len(views)}):")
    print("-" * 80)
    for v in views:
        print(f"  • {v['table_name']}")
    
    # ========================================================================
    # Get columns for each table
    # ========================================================================
    print(f"\n📋 TABLE STRUCTURES:")
    print("=" * 80)
    
    for t in tables:
        table_name = t['table_name']
        
        columns = await conn.fetch("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = $1
            ORDER BY ordinal_position;
        """, table_name)
        
        print(f"\n🗂️  {table_name.upper()}")
        print("-" * 80)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:30} {col['data_type']:20} {nullable:10}{default}")
        
        # Get row count
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name};")
        print(f"\n  📊 Rows: {count}")
    
    # ========================================================================
    # Get foreign key relationships
    # ========================================================================
    print(f"\n\n🔗 FOREIGN KEY RELATIONSHIPS:")
    print("=" * 80)
    
    fks = await conn.fetch("""
        SELECT
            tc.table_name AS from_table,
            kcu.column_name AS from_column,
            ccu.table_name AS to_table,
            ccu.column_name AS to_column,
            tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name;
    """)
    
    for fk in fks:
        print(f"\n  {fk['from_table']}.{fk['from_column']}")
        print(f"    └─> {fk['to_table']}.{fk['to_column']}")
        print(f"        ({fk['constraint_name']})")
    
    await conn.close()
    
    print("\n" + "=" * 80)
    print("✅ Inspection Complete")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(inspect_database())
