# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify
import sqlalchemy
import time
# web app
app = Flask(__name__)

# database engine
engine = sqlalchemy.create_engine(os.getenv('SQL_URI'))

#Controls RATE_NUM requests per RATE_TIME
#ex. RATE_TIME = 60 and RATE_NUM = 2
#    results in 2 requests every 60 seconds limit
RATE_TIME = 60
RATE_NUM = 2
REQUEST_HISTORY = []

@app.route('/')
def index():
    return 'Welcome to EQ Works 😎'


@app.route('/events/hourly')
def events_hourly():
    return queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/events/daily')
def events_daily():
    return queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')


@app.route('/stats/hourly')
def stats_hourly():
    return queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/stats/daily')
def stats_daily():
    return queryHelper('''
        SELECT date,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            SUM(revenue) AS revenue
        FROM public.hourly_stats
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')

@app.route('/poi')
def poi():
    return queryHelper('''
        SELECT *
        FROM public.poi;
    ''')

def queryHelper(query):
    with engine.connect() as conn:
        if rateLimitCheck():
            result = conn.execute(query).fetchall()
            return jsonify([dict(row.items()) for row in result])
        else:
            return "You are doing that too often"
def rateLimitCheck():
    rateFlag = False
    currTime = int(time.time())
    #clear stack
    while len(REQUEST_HISTORY) > 0  and currTime - REQUEST_HISTORY[0] > RATE_TIME:
        REQUEST_HISTORY.pop(0)
    if len(REQUEST_HISTORY) < RATE_NUM:
        rateFlag = True
        REQUEST_HISTORY.append(currTime)

    return rateFlag
      
