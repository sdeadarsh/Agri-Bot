from flask import Flask, request, json, Response, jsonify, make_response
from apscheduler.schedulers.background import BackgroundScheduler
import app
import helper

if __name__ == "__main__":
    app = Flask('runib')
    scheduler = BackgroundScheduler()
    scheduler.add_job(id='Scheduled Task', func=helper.solr_full_import, trigger="interval", hours=24)
    scheduler.start()

app.run()
