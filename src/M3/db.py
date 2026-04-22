
# from pymongo import MongoClient
# import streamlit as st


# def get_database():
#     client = MongoClient(st.secrets["MONGO_URI"])
#     return client["m3_pediatric_db"]
 

# new one 
import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

# This tells Python to look for the .env file in the SAME folder as this db.py file
base_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

_client: MongoClient | None = None

def get_database() -> Database:
    global _client
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        # This is where your error is currently triggering
        raise RuntimeError(f"MONGO_URI not found. Looked in: {dotenv_path}")
        
    clean_uri = mongo_uri.strip().strip('"').strip("'")
    
    if _client is None:
        _client = MongoClient(clean_uri)
        
    return _client["m3_pediatric_db"]