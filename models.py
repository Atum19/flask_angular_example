# from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client.WordsData
# connect('mongodb://localhost:27017/WordsData')
