
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os


# Load the environment variables
load_dotenv()

uri = os.getenv("uri")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Create a new database
db = client['tasks']
task_collection = db['tasks']

