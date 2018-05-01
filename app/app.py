import datetime
import os
import sqlalchemy
import logging
import json
import time

from flask import Flask, jsonify
from flask import request
from flask import make_response, redirect
from flask_sqlalchemy import SQLAlchemy

from outbreak_detection import outbreak_detector, disease_regressor
from response_db import *


DBUSER = 'marco'
DBPASS = 'foobarbaz'
DBHOST = 'database'
DBPORT = '5432'
DBNAME = 'testdb'


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'foobarbaz'


db = SQLAlchemy(app)


class SymptomObservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime())
    symptom = db.Column(db.String(146))
    occurrences = db.Column(db.Integer)

# Make sure database tables are created.
# TODO: This not very clean.
dbstatus = False
while not dbstatus:
    try:
        db.create_all()
    except:
        time.sleep(2)
    else:
        dbstatus = True


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello Docker!'


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

@app.route('/bot')
def bot():
    return redirect("https://bot.dialogflow.com/ee501930-f67e-4cfd-b812-5145f632b1e1", code=302)

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
    action = result.get('action')
    parameters = result.get('parameters')
    contexts = result.get('outputContexts')

    if action in info_response_db.keys():
        fulfillment_text = info_response_db.get(action).get(parameters.get('disease'))
    elif action == 'report.symptom':
        store_symptoms_in_db(parameters, db)
        outbreak_report = check_for_outbreak()
        fulfillment_text = report_response_db['report.symptom.opening']

        for disease, outbreak in outbreak_report.items():
            if outbreak:
                fulfillment_text += report_response_db['warning.doctor'].format(disease)

        fulfillment_text += report_response_db['report.symptom.closing'].format(disease)

    elif action == 'epidemics.information':
        outbreak_report = check_for_outbreak()
        fulfillment_text = ''
        for disease, outbreak in outbreak_report.items():
            if outbreak:
                fulfillment_text += info_response_db['epidemics.information.epidemic'].format(disease)
        if not fulfillment_text:
            fulfillment_text = info_response_db['epidemics.information.ok']

    else:
        fulfillment_text = info_response_db['default']

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


def check_for_outbreak():
    disease_prediction = get_prediction()
    outbreak_report = outbreak_detector.detect(disease_prediction)
    return outbreak_report


def get_prediction():
    symptoms_observations = get_symptom_observation_from_last_week()
    symptoms_observations_dict = format_observations_as_dict(symptoms_observations)
    disease_prediction = disease_regressor.predict(symptoms_observations_dict)
    return disease_prediction


@app.route('/last_week')
def last_week():
    symptoms_observations = get_symptom_observation_from_last_week()
    results = ['{} {}'.format(entry.symptom, entry.occurrence_count)
               for entry in symptoms_observations]
    output = '\n'.join(results)

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def get_symptom_observation_from_last_week():
    current_time = datetime.datetime.utcnow()
    one_week_ago = current_time - datetime.timedelta(minutes=2)  # TODO Only two minutes for demonstration purposes.
    summed_symptoms_observations = (
        db.session.query(SymptomObservation.symptom,
                         sqlalchemy.func.sum(SymptomObservation.occurrences).label('occurrence_count'))
            .filter(SymptomObservation.timestamp > one_week_ago)
            .group_by(SymptomObservation.symptom)
            .all()
    )
    return summed_symptoms_observations


def format_observations_as_dict(observations):
    observation_dict = {
        'Ausschlag an Haut oder Schleimhaut mit Flecken, Bläschen oder Pusteln außer Herpes zoster': 0,
        'Ausschlag an Haut oder Schleimhaut mit gleichzeitig vorhandenen Papeln, Bläschen bzw. Pusteln und Schorf sog. Sternenhimmel': 0,
        'Ausschlag, einseitig auf Hautsegment beschränkt, bläschenförmig': 0,
        'Brennen, Juckreiz': 0,
        'Durchfall und/oder Erbrechen': 0,
        'Durchfall, nicht näher bezeichnet': 0,
        'Fetales kongenitales Varizellensyndrom': 0,
        'Fieber': 0,
        'Gliederschmerzen': 0,
        'Husten': 0,
        'Muskel-, Glieder-, Rücken- oder Kopfschmerzen': 0,
        'Pneumonie Lungenentzündung': 0,
        'Schmerzen im betroffenen Bereich Zosterneuralgie': 0,
        'Schmerzen, einseitig auf ein Hautsegment lokalisiert, ohne Ausschlag': 0,
        'akuter Krankheitsbeginn': 0,
        'akutes schweres Atemnotsyndrom ARDS': 0,
        'andere Symptome': 0,
        'beatmungspflichtige Atemwegserkrankung': 0}

    for observation in observations:
        observation_dict[observation.symptom] = observation.occurrence_count

    return {'symptoms': observation_dict}


@app.route('/predict')
def predict():
    disease_prediction = get_prediction()

    return jsonify(disease_prediction), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/predict_from_symptoms', methods=['POST'])
def predict_from_symptoms():
    req = request.get_json(silent=True, force=True)
    disease_prediction = disease_regressor.predict(req)

    return jsonify(disease_prediction), 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/delete')
def delete():
    try:
        db.session.query(SymptomObservation).delete()
        db.session.commit()
    except:
        db.session.rollback()

    return 'all entries deleted', 200, {'Content-Type': 'text/plain; charset=utf-8'}


if __name__ == '__main__':

    dbstatus = False
    while dbstatus == False:
        try:
            db.create_all()
        except:
            time.sleep(2)
        else:
            dbstatus = True
    app.run(debug=True, host='0.0.0.0')
