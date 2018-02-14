from flask import Flask
from flask import request
from flask import jsonify
import pickle
import numpy as np
app = Flask(__name__)

rf_model = pickle.load(open('random_forest_18.pkl', 'rb'))
# mean thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 2219}
# handpicked:
thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 1800}

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data_json = request.json
        data = np.array(list(data_json['symptoms'].values())).reshape(1, -1) 
        print("This is the data put into the model: "+str(data)+ " "+str(type(data))+ " "+str(data.shape))
        prediction = rf_model.predict(data)
        prediction_dict = {
            'Influenza': prediction[0][0], 
            'Windpocken': prediction[0][1], 
            'Norovirus-Gastroenteritis': prediction[0][2]
        }

        print("hallo")

    return jsonify(prediction_dict)

# @app.route('/evaluate', methods=['POST'])
# def predict():
#     if request.method == 'POST':
#         data_json = request.json