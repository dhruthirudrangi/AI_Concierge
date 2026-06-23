from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

db = client["credit_card_recommendation"]

cards_collection = db["cards"]