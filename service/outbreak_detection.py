import pickle
import numpy as np


class DiseaseRegressor:
    """Predict number of diseases based on number of symptoms."""

    def __init__(self, model):
        self._model = model

    def predict(self, symptoms_data) -> dict:
        """
        Given the current distribution of symptoms, this method returns the estimated distribution of diseases.
        """

        key_list = list(symptoms_data['symptoms'].keys())
        print('key_list', key_list)
        key_list.sort()
        data = np.zeros(18)
        for i, key in enumerate(key_list):
            data[i] = symptoms_data['symptoms'][key]
        data = data.reshape(1, -1)
        print("This is the data put into the model: " + str(data) + " " + str(type(data)) + " " + str(data.shape))
        prediction = self._model.predict(data)
        prediction_dict = {
            'Influenza': prediction[0][0],
            'Windpocken': prediction[0][1],
            'Norovirus-Gastroenteritis': prediction[0][2]
        }

        return prediction_dict


class OutbreakDetector:
    """Abstract base class."""
    def detect(self, data):
        raise NotImplementedError


class ThresholdOutbreakDetector(OutbreakDetector):

    def __init__(self, thresholds):
        self._thresholds = thresholds

    def detect(self, data):
        """
        Given the current distribution of diseases, this method returns a dict with a truth value for every given disease. True means that the number of cases
        is over a specific value that we determined as report-worthy.
        """
        report = {}

        for key in data.keys():
            if data[key] > thresholds[key]:
                report[key] = True
            else:
                report[key] = False

        return report


disease_regressor = DiseaseRegressor(pickle.load(open('random_forest_18.pkl', 'rb')))
# mean thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 2219}
# handpicked:
# thresholds = {'Influenza': 853, 'Windpocken': 178, 'Norovirus-Gastroenteritis': 1800}
# toy
thresholds = {'Influenza': 20, 'Windpocken': 10, 'Norovirus-Gastroenteritis': 20}

outbreak_detector = ThresholdOutbreakDetector(thresholds)


# @app.route('/predict', methods=['POST'])
# def give_prediction():
#     data_json = request.json
#     return jsonify(predict(data_json))
#
#
# @app.route('/evaluate', methods=['POST'])
# def evaluate():
#     data_json = request.json
#     data = predict(data_json)
#     return jsonify(threshold_report(data))
