import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, jsonify, request
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
import json

from rq import Queue
from rq.job import Job
from worker import conn

from models import db

q = Queue(connection=conn)

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])

# client = MongoClient('localhost:27017')
# db = client.WordsData


def count_and_save_words(url):

    errors = []
    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    # text processing
    raw = BeautifulSoup(r.text).get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w.encode('utf-8') for w in text if nonPunct.match(w)]
    # raw_word_count = Counter(raw_words)
    raw_word_count = dict((k.decode('utf-8').replace('.', '_'), v)
                          for (k, v) in Counter(raw_words).most_common(10))

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = dict((k.decode('utf-8').replace('.', '_'), v)
                               for (k, v) in Counter(no_stop_words).most_common(10))

    # save the results
    try:
        result = db.data_count.insert_one(
            {
                "url": url,
                "result_all": raw_word_count,
                "result_no_stop_words": no_stop_words_count,
            }
        )

        return result.inserted_id
    except Exception as e:
        errors.append("Unable to add item to database ")
        print('-------------------- error: ', errors, e)
        return {"error": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http' not in url[:7]:
        url = 'https://' + url

    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    # return created job id
    print('@@@@@@@@@@@@@ >>>', job.get_id())
    return job.get_id()


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    # print('########## 111', job._status)
    # print('########## 0000', job.get_status())
    # print('########## 222', job.is_started)
    # print('########## 333', job.is_finished)
    # print('########## 444', job.result())

    if job.is_finished:

        result = db.data_count.find()[0]["result_no_stop_words"]

        db.data_count.drop()
        return jsonify(result)
    else:
        return "Nay!", 202

if __name__ == '__main__':
    app.run()
