# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify
import sqlalchemy
import time
from rate_limit import RateLimit, RateLimitManager
# web app
app = Flask(__name__)

# database engine
engine = sqlalchemy.create_engine(os.getenv('SQL_URI'))

#instantiate rate limit manager
rateManager = RateLimitManager()

@app.route('/')
def index():
    return 'Welcome to EQ Works 😎'


@app.route('/events/hourly')
@rateManager.limit(rateNum=2,rateTime=60)
def events_hourly():
    return queryHelper('''
        SELECT date, hour, events
        FROM public.hourly_events
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/events/daily')
@rateManager.limit(rateNum=2,rateTime=60)
def events_daily():
    return queryHelper('''
        SELECT date, SUM(events) AS events
        FROM public.hourly_events
        GROUP BY date
        ORDER BY date
        LIMIT 7;
    ''')


@app.route('/stats/hourly')
@rateManager.limit(rateNum=2,rateTime=120)
def stats_hourly():
    return queryHelper('''
        SELECT date, hour, impressions, clicks, revenue
        FROM public.hourly_stats
        ORDER BY date, hour
        LIMIT 168;
    ''')


@app.route('/stats/daily')
@rateManager.limit(rateNum=1,rateTime=10)
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
@rateManager.limit(rateNum=-1,rateTime=-1)
def poi():
    return queryHelper('''
        SELECT *
        FROM public.poi;
    ''')

def queryHelper(query):
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        return jsonify([dict(row.items()) for row in result])
