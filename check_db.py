import certifi
from pymongo import MongoClient

try:
    client = MongoClient(
        "mongodb+srv://swethas2005:Hello2005@cluster0.tbxmbbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        tls=True,
        tlsCAFile=certifi.where()
    )
    db = client["shebuilds_db"]
    problems_collection = db["problems"]
    
    count = problems_collection.count_documents({})
    print(f"Total problems in DB: {count}")
    
    if count > 0:
        print("Sample problem:")
        print(problems_collection.find_one())
    else:
        print("No problems found. Creating a dummy problem...")
        problems_collection.insert_one({
            "ticket_number": 12345,
            "category": "Plumbing",
            "days_facing_issue": 2,
            "description": "Test leakage from script",
            "engdescription": "Test leakage from script",
            "status": "Pending",
            "user_email": "test@example.com",
            "handleby": None
        })
        print("Dummy problem created.")

except Exception as e:
    print(f"Error: {e}")
