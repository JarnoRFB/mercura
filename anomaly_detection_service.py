import pickle

import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

rf_model = pickle.load(open('random_forest_18.pkl', 'rb'))
# mean thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 2219}
# handpicked:
thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 1800}

def predict(data_json):
    """
    given the current distribution of symptoms, this method returns the estimated distribution of diseases
    """
    if request.method == 'POST':
        
        key_list = list(data_json['symptoms'].keys())
        key_list.sort()
        data = np.zeros([len(key_list)])
        for i, key in enumerate(key_list):
            data[i] = data_json['symptoms'][key]
        data = data.reshape(1, -1)
        print("This is the data put into the model: "+str(data)+ " "+str(type(data))+ " "+str(data.shape))
        prediction = rf_model.predict(data)
        prediction_dict = {
            'Influenza': prediction[0][0], 
            'Windpocken': prediction[0][1], 
            'Norovirus-Gastroenteritis': prediction[0][2]
        }

    return prediction_dict

def threshold_report(data):
    """
    given the current distribution of diseases, this method returns a json with a truth value for every given disease. True means that the number of cases
    is over a specific value that we determined as report-worthy
    """
    if request.method == 'POST':
        report = {}
        
        for key in data.keys():
            if data[key]>thresholds[key]:
                report[key] = True
            else:
                report[key] = False
    return report



@app.route('/predict', methods=['POST'])
def give_prediction():
    data_json = request.json
    return jsonify(predict(data_json))




@app.route('/evaluate', methods=['POST'])
def evaluate():
    data_json = request.json
    data = predict(data_json)
    return jsonify(threshold_report(data))




