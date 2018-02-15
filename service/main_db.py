import datetime
import os

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

import logging

import json

from flask import Flask
from flask import request
from flask import make_response


response_db = {
    'prevention.information':
         {'Influenza': 'Nicht husten!'},
    'report.symptom': 'Vielen Dank für Ihren Report!',
    'default': 'Tut mir leid, darauf kann ich nicht antworten'
}


app = Flask(__name__)

# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class SymptomObservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime())
    symptom = db.Column(db.String(146))
    occurrences = db.Column(db.Integer)



@app.route('/')
def index():


    symptom_observation = SymptomObservation(
        symptom='Durchfall',
        timestamp=datetime.datetime.utcnow(),
        occurrences=4
    )

    db.session.add(symptom_observation)
    db.session.commit()

    symptoms = SymptomObservation.query.order_by(sqlalchemy.desc(SymptomObservation.timestamp)).limit(10)

    results = [
        'Zeit: {} Symptom: {} Anzahl: {}'.format(symptom.timestamp, symptom.symptom, symptom.occurrences)
        for symptom in symptoms]

    output = 'Last 10 visits:\n{}'.format('\n'.join(results))

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/webhook')
def webhook():


    symptom_observation = SymptomObservation(
        symptom='Durchfall',
        timestamp=datetime.datetime.utcnow(),
        occurrences=4
    )

    db.session.add(symptom_observation)
    db.session.commit()

    symptoms = SymptomObservation.query.order_by(sqlalchemy.desc(SymptomObservation.timestamp)).limit(10)

    results = [
        'Zeit: {} Symptom: {} Anzahl: {}'.format(symptom.timestamp, symptom.symptom, symptom.occurrences)
        for symptom in symptoms]

    output = 'Last 10 visits:\n{}'.format('\n'.join(results))

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}




@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = make_webhook_result(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def make_webhook_result(request):
    result = request.get("queryResult")
    print('result')
    print(result.keys())
    action = result.get('action')
    parameters = result.get('parameters')
    contexts = result.get('outputContexts')
    print('contexts')
    print(contexts)


    if action == 'prevention.information':
        fulfillment_text = response_db.get(action).get(parameters.get('disease'))
    elif action == 'report.symptom':
        store_symptoms_in_db(parameters, db)
        fulfillment_text = response_db[action]
    else:
        fulfillment_text = response_db['default']

    return {
        "fulfillmentText": fulfillment_text,
    }

def store_symptoms_in_db(parameters, db):
    symptom_observation = SymptomObservation(
        symptom=parameters['symptom'],
        timestamp=datetime.datetime.utcnow(),
        occurrences=parameters['occurrences']
    )

    db.session.add(symptom_observation)
    db.session.commit()

@app.route('/symptoms_db')
def symptoms_db():
    symptoms = SymptomObservation.query.order_by(sqlalchemy.desc(SymptomObservation.timestamp))

    results = [
        'Zeit: {} Symptom: {} Anzahl: {}'.format(symptom.timestamp, symptom.symptom, symptom.occurrences)
        for symptom in symptoms]

    output = '\n'.join(results)

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
