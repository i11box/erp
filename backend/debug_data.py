#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Step 1: Starting script")

try:
    print("Step 2: Importing database modules")
    from app.database import engine, SessionLocal, Base
    print("Step 3: Database modules imported successfully")

    print("Step 4: Creating database tables")
    Base.metadata.create_all(bind=engine)
    print("Step 5: Database tables created successfully")

    print("Step 6: Creating database session")
    db = SessionLocal()
    print("Step 7: Database session created successfully")

    print("Step 8: Importing models")
    from app.models import Product
    print("Step 9: Models imported successfully")

    print("Step 10: Querying existing products")
    existing_products = db.query(Product).all()
    print(f"Step 11: Found {len(existing_products)} existing products")

    db.close()
    print("Step 12: Script completed successfully")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()