import datetime
import os
import sqlalchemy
import logging
import json

from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

from outbreak_detection import outbreak_detector, disease_regressor

response_db = {
    'prevention.information':
        {'Influenza': 'Nicht husten!'},
    'report.symptom': 'Vielen Dank für Ihren Report!',
    'warning.doctor': ' Achtung! Erhöhtes Vorkommen von {} in Ihrer Stadt.',
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
        outbreak_report = check_for_outbreak()
        fulfillment_text = response_db[action]

        for disease, outbreak in outbreak_report.items():
            if outbreak:
                fulfillment_text += response_db['warning.doctor'].format(disease)



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


def check_for_outbreak():
    symptoms_observations = get_symptom_observation_from_last_week()
    print('symptoms_observations ', symptoms_observations)
    if symptoms_observations:
        symptoms_observations_dict = format_observations_as_dict(symptoms_observations)
        print('symptoms_observations_dict', symptoms_observations_dict)
        disease_prediction = disease_regressor.predict(symptoms_observations_dict)
        outbreak_report = outbreak_detector.detect(disease_prediction)
        print('outbreak_report', outbreak_report)
    return outbreak_report


@app.route('/last_week')
def last_week():
    symptoms_observations = get_symptom_observation_from_last_week()
    results = ['{} {}'.format(entry.symptom, entry.occurrence_count)
               for entry in symptoms_observations]
    output = '\n'.join(results)

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def get_symptom_observation_from_last_week():
    current_time = datetime.datetime.utcnow()
    one_week_ago = current_time - datetime.timedelta(minutes=2)
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
        'Ausschlag an Haut oder Schleimhaut mit Flecken, Bläschen oder Pusteln (außer Herpes zoster)': 0,
        'Ausschlag an Haut oder Schleimhaut mit gleichzeitig vorhandenen Papeln, Bläschen bzw. Pusteln und Schorf (sog. Sternenhimmel)': 0,
        'Ausschlag, einseitig auf Hautsegment beschränkt, bläschenförmig': 0,
        'Brennen, Juckreiz': 0,
        'Durchfall und/oder Erbrechen': 0,
        'Durchfall, nicht näher bezeichnet': 0,
        'Fetales (kongenitales) Varizellensyndrom': 0,
        'Fieber': 0,
        'Gliederschmerzen': 0,
        'Husten': 0,
        'Muskel-, Glieder-, Rücken- oder Kopfschmerzen': 0,
        'Pneumonie (Lungenentzündung)': 0,
        'Schmerzen im betroffenen Bereich (Zosterneuralgie)': 0,
        'Schmerzen, einseitig auf ein Hautsegment lokalisiert, ohne Ausschlag': 0,
        'akuter Krankheitsbeginn': 0,
        'akutes schweres Atemnotsyndrom (ARDS)': 0,
        'andere Symptome': 0,
        'beatmungspflichtige Atemwegserkrankung': 0}

    for observation in observations:
        observation_dict[observation.symptom] = observation.occurrence_count

    return {'symptoms': observation_dict}


@app.route('/symptoms-db')
def symptoms_db():
    symptoms_observations = SymptomObservation.query.order_by(sqlalchemy.desc(SymptomObservation.timestamp))

    results = [
        'Zeit: {} Symptom: {} Anzahl: {}'.format(symptom.timestamp, symptom.symptom, symptom.occurrences)
        for symptom in symptoms_observations]

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
