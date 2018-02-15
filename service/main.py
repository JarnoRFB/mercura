# Original Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import json

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

response_db = {
    'prevention.information':
         {
        'Influenza': 'Influenza-Viren übertragen sich durch Tröpfcheninfektion und sind dadurch extrem ansteckend. Halten Sie sich von erkrankten Personen fern und waschen sie sich oft die Hände. Es gibt auch Impfmöglichkeiten.',
        'Noro-Gastroenteritis': 
            '''Noro-Viren werden hauptsächlich über 3 verschiedene Arten übertragen: 
            direkt von Mensch zu Mensch, indirekt über verunreinigte Gegenstände und indirekt über Nahrungsmittel.    
            Je nachdem muss man sich anders schützen. Worüber möchten sie mehr erfahren?''',
         'Windpocken': 'Vor dem Windpocken-Virus schützen Sie sich am Besten indem Sie sich von Erkrankten Personen fernhalten oder sich impfen lassen.'
         },
    'prevention.information.schmierinfektion1':
        {'Noro-Gastroenteritis': 
            '''Kranke Menschen haben oft Viren an ihren Händen oder verbreiten beim Erbrechen Viren über die Luft. 
            Halten Sie sich also von Kranken fern und falls sie doch in Kontakt kommen, waschen Sie sich die Hände.''',
        'Influenza': '',
        'Windpocken': ''},
    'prevention.information.schmierinfektion2':
        {'Noro-Gastroenteritis': 
            '''Fassen erkrankte Menschen Gegenstände wie Türknäufe, Geländer und Armaturen an,
            hinterlassen sie dort Viren, die dort mehrere Tage überleben können. Vermeiden sie also den
             Kontakt mit diesen Objekten oder waschen sie sich danach die Hände.''',
        'Windpocken': '',
        'Influenza': ''
        },
    'prevention.information.schmierinfektion3':
        {'Noro-Gastroenteritis': 
            '''Erkrankte Menschen können auch in Lebensmitteln und Flüssigkeiten Viren hinterlassen. Vermeiden Sie also öffentlichen Gewässer und Gefahrenherde wie
            Buffets. Überprüfen Sie auch, wer ihr Essen zubereitet hat.''',
        'Windpocken': '',
        'Influenza': ''
        },       
    'prevention.information.with.context':
        {
        'Influenza': 'Influenza-Viren übertragen sich durch Tröpfcheninfektion und sind dadurch extrem ansteckend. Halten Sie sich von erkrankten Personen fern und waschen sie sich oft die Hände. Es gibt auch Impfmöglichkeiten.',
        'Noro-Gastroenteritis': 
            '''Noro-Viren werden hauptsächlich über 3 verschiedene Arten übertragen: 
            direkt von Mensch zu Mensch, indirekt über verunreinigte Gegenstände und indirekt über Nahrungsmittel.    
            Je nachdem muss man sich anders schützen. Worüber möchten sie mehr erfahren?''',
         'Windpocken': 'Vor dem Windpocken-Virus schützen Sie sich am Besten indem Sie sich von Erkrankten Personen fernhalten oder sich impfen lassen.'
        },    
    'symptom.information':
        {
        'Influenza': 'Sind sie sich unsicher ob sie vielleicht die Grippe haben?',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        },   
    'symptom.information.influenza':
        {
        'Influenza': 'Von einer normalen Erkältung, die man auch grippalen Infekt nennt, unterscheidet sich die "echte" Grippe, die sogenannte Influenza, besonders durch ihren plötzlichen Beginn. Möchten Sie mehr erfahren?',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        },   
    'symptom.information.influenza.more':
        {
        'Influenza': 'Bei einem grippalen Infekt, kündigen sich erste Symptome, wie Schnupfen, Halsschmerzen und gelegentliche Kopfschmerzen oft schon früh an. Eine Influenza beginnt jedoch mit plötzlichem Fieber, Schwächegefühl und Kopf- und Gliederschmerzen. Kann ich dir noch irgendwie helfen?',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        }, 
    'symptom.information.with.context':
        {
        'Influenza': 'Sind sie sich unsicher ob sie vielleicht die Grippe haben?',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        },   
    'duration':
        {
        'Influenza': 'Bei einem unkomplizierten Verlauf halten die Beschwerden etwa 5 bis 7 Tage an.',
        'Noro-Gastroenteritis': 
            '''Von der Ansteckung bis zu ersten Symptomen können zwischen 6 und 48 Stunden vergehen. Die akute Phase danach dauert normalerweise 12 bis 48 Stunden. Nach Abklingen der Symptome ist man allerdings noch weitere 48 Stunden ansteckend.''',
         'Windpocken': '''14 bis 17 Tage nach der Ansteckung können die ersten Symptome auftreten. Sind die Windpocken erst einmal ausgebrochen,
          dauert es meist zwischen fünf und zehn Tagen, bis die letzten Bläschen verkrustet und die Erkrankung somit nicht mehr ansteckend ist.'''
        },   
    'duration.with.context':
        {
        'Influenza': 'Bei einem unkomplizierten Verlauf halten die Beschwerden etwa 5 bis 7 Tage an.',
        'Noro-Gastroenteritis': 
            '''Von der Ansteckung bis zu ersten Symptomen können zwischen 6 und 48 Stunden vergehen. Die akute Phase danach dauert normalerweise 12 bis 48 Stunden. Nach Abklingen der Symptome ist man allerdings noch weitere 48 Stunden ansteckend.''',
         'Windpocken': '14 bis 17 Tage nach der Ansteckung können die ersten Symptome auftreten. Sind die Windpocken erst einmal ausgebrochen, dauert es meist zwischen fünf und zehn Tagen, bis die letzten Bläschen verkrustet und die Erkrankung somit nicht mehr ansteckend ist.'
        }, 
    'complications':
        {
        'Influenza': 'Als häufigste Komplikationen werden Lungenentzündungen gefürchtet. Bei Kindern können sich auch Mittelohrentzündungen entwickeln. Selten können Entzündungen des Gehirns oder des Herzmuskels auftreten.',
        'Noro-Gastroenteritis': 
            '''Besonders bei Risikopatienten kann der extreme Flüssigkeitsmangel durch den Brechdurchfall von Kreislaufproblemen über Kollaps bis zu Nierenversagen führen. Sorgen Sie dafür, dass Sie ausreichend trinken''',
         'Windpocken': 'Es können manchmal bakterielle Infektionen der Haut auftreten. Besonders bei schwangeren Frauen ist eine Lungenentzündung als Folge von Windpocken gefürchtet. Ganz selten ist auch das zentrale Nervensystem von der Infektion betroffen.'
        },  
    'complications.with.context':
        {
        'Influenza': 'Als häufigste Komplikationen werden Lungenentzündungen gefürchtet. Bei Kindern können sich auch Mittelohrentzündungen entwickeln. Selten können Entzündungen des Gehirns oder des Herzmuskels auftreten.',
        'Noro-Gastroenteritis': 
            '''Besonders bei Risikopatienten kann der extreme Flüssigkeitsmangel durch den Brechdurchfall von Kreislaufproblemen über Kollaps bis zu Nierenversagen führen. Sorgen Sie dafür, dass Sie ausreichend trinken''',
         'Windpocken': 'Es können manchmal bakterielle Infektionen der Haut auftreten. Besonders bei schwangeren Frauen ist eine Lungenentzündung als Folge von Windpocken gefürchtet. Ganz selten ist auch das zentrale Nervensystem von der Infektion betroffen.'
        },  
    'go.to.doctor':
        {
        'Influenza': 'Wenn die Krankheitszeichen plötzlich einsetzen und das Allgemeinbefinden schwer beeinträchtigen, ist es ratsam direkt eine Ärztin oder einen Arzt aufzusuchen. Besonders bei anhaltend hohem Fieber sollte spätestens ab dem dritten Erkrankungstag eine Arztpraxis aufgesucht werden.',
        'Noro-Gastroenteritis': 
            '''Wenn starke Kreislaufprobleme auftreten oder Muskelkrämpfe, Schläfrigkeit oder Verwirrtheit sowie hohes Fieber, sollte in jedem Fall eine Ärztin oder Arzt zu Rate gezogen werden. Das gleiche gilt für den Fall, dass Blut im Stuhl auftritt oder dass der Brechdurchfall länger als drei Tage anhält.''',
         'Windpocken': ''
        },  
    'go.to.doctor.with.context':
        {
        'Influenza': 'Wenn die Krankheitszeichen plötzlich einsetzen und das Allgemeinbefinden schwer beeinträchtigen, ist es ratsam direkt eine Ärztin oder einen Arzt aufzusuchen. Besonders bei anhaltend hohem Fieber sollte spätestens ab dem dritten Erkrankungstag eine Arztpraxis aufgesucht werden.',
        'Noro-Gastroenteritis': 
            '''Wenn starke Kreislaufprobleme auftreten oder Muskelkrämpfe, Schläfrigkeit oder Verwirrtheit sowie hohes Fieber, sollte in jedem Fall eine Ärztin oder Arzt zu Rate gezogen werden. Das gleiche gilt für den Fall, dass Blut im Stuhl auftritt oder dass der Brechdurchfall länger als drei Tage anhält.''',
         'Windpocken': ''
        },  
    'vaccination.information':
        {
        'Influenza': '',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        },  
    'vaccination.information.with.context':
        {
        'Influenza': '',
        'Noro-Gastroenteritis': 
            '''''',
         'Windpocken': ''
        },  


    'default': 'Tut mir leid, darauf kann ich nicht antworten'
} 




@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello Appengine!'


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


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
    elif action == 'prevention.information.schmierinfektion3':
        fulfillment_text = response_db.get(action).get(parameters.get('disease'))
    else:
        fulfillment_text = response_db['default']

    return {
        "fulfillmentText": fulfillment_text,
    }


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
