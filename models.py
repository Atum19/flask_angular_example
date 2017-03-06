from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from pymongo import MongoClient

# client = MongoClient('localhost:27017')
# db = client.WordsData
connect('mongodb://localhost:27017/WordsData')


# class Result(db.Model):
class Result(MongoModel):
    __tablename__ = 'WordsData'

    url = fields.URLField()
    result_all = fields.DictField()
    result_no_stop_words = fields.DictField()
