"""
Migration script to convert plan IDs from strings to numeric primary keys.
This script:
1. Creates a new plans table with numeric IDs
2. Copies all data from old table
3. Renames tables
"""

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from main import engine

def migrate_to_numeric_ids():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Starting migration to numeric IDs...")
            
            # Create new table structure
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS plans_new (
                    id SERIAL PRIMARY KEY,
                    old_id VARCHAR UNIQUE,
                    short_name VARCHAR NOT NULL,
                    full_name VARCHAR NOT NULL,
                    summary_of_benefits TEXT,
                    summary_of_benefits_url TEXT,
                    compressed_summary TEXT,
                    plan_type TEXT,
                    plan_document_full_text TEXT,
                    summary_of_benefit_coverage TEXT,
                    table_of_contents TEXT,
                    document_type VARCHAR(20)
                )
            """))
            print("Created new table structure")
            
            # Copy data from old table to new table
            conn.execute(text("""
                INSERT INTO plans_new (
                    old_id, short_name, full_name, summary_of_benefits,
                    summary_of_benefits_url, compressed_summary, plan_type,
                    plan_document_full_text, summary_of_benefit_coverage,
                    table_of_contents, document_type
                )
                SELECT 
                    id, short_name, full_name, summary_of_benefits,
                    summary_of_benefits_url, compressed_summary, plan_type,
                    plan_document_full_text, summary_of_benefit_coverage,
                    table_of_contents, document_type
                FROM plans
                ORDER BY 
                    CASE plan_type
                        WHEN 'Medicaid' THEN 1
                        WHEN 'Dual Eligible' THEN 2
                        WHEN 'Medicare' THEN 3
                        WHEN 'Marketplace' THEN 4
                        ELSE 5
                    END,
                    short_name
            """))
            print("Copied data to new table")
            
            # Drop old table and rename new table
            conn.execute(text("DROP TABLE plans"))
            conn.execute(text("ALTER TABLE plans_new RENAME TO plans"))
            print("Renamed tables")
            
            # Show the new data
            result = conn.execute(text("""
                SELECT id, old_id, short_name, plan_type 
                FROM plans 
                ORDER BY id
            """))
            
            print("\nMigration complete! New plan IDs:")
            print("-" * 60)
            print(f"{'ID':<5} {'Old ID':<25} {'Short Name':<15} {'Type':<15}")
            print("-" * 60)
            for row in result:
                print(f"{row[0]:<5} {row[1]:<25} {row[2]:<15} {row[3] or 'N/A':<15}")
            
            trans.commit()
            
        except Exception as e:
            trans.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_to_numeric_ids()