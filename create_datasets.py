import numpy as np
import pandas as pd
import pickle as pk

from sklearn.model_selection import train_test_split as split_data


class SymptomDiseaseData:
    def __init__(self):
        self.symptoms_data = []
        self.disease_data = []
        self.BREAKOFF = False
        self.overall_week = 0

        self._load_data()
    
    def _load_data(self):
        self.weekly_symptoms = pk.load(open("weekly_symptoms.pkl", "rb"))
        self.weekly_diseases = pk.load(open("weekly_diseases.pkl", "rb"))
        self.weekly_diseases = self.weekly_diseases.drop(columns='Kalenderwoche')
        self.weekly_diseases = self.weekly_diseases.loc[:, ('Influenza', 'Windpocken', 'Norovirus-Gastroenteritis')]

    def generate_data(self, split=True):
        """
        Puts symptoms and diseases in numpy arrays, splits into train, val, and test sets, or just returns all data
        if you want.
        Args:
            split: if data should be split into training/test etc
        Returns:
            train, val, test, train_label, val_label, test_label
        """
        for year in range(2001,2019):
            for week in range(1, 53):
                if year == 2018:
                    if week == 6:
                        self.BREAKOFF = True

                if week < 10:
                    week = '0'+str(week)
                else:
                    week = str(week)

                date = str(year)+'-KW'+week
                #print("Appending:", date) # for debugging

                self.symptoms_data.append(list(self.weekly_symptoms.loc[self.weekly_symptoms['Kalenderwoche'] == date]['Anzahl'][:18]))
                self.disease_data.append(list(self.weekly_diseases.iloc[self.overall_week]))

                self.overall_week += 1

                if self.BREAKOFF:
                    break

        self.symptoms_data = np.asarray(self.symptoms_data)
        self.disease_data = np.asarray(self.disease_data)
        if split:
            self._split()
            return self.train, self.valid, self.test, self.train_labels, self.valid_labels, self.test_labels
        else:
            return self.symptoms_data, self.disease_data

    def _split(self):
        """
        Splits data and labels into training, validation, and test sets.
        """
        self.train, valtest, self.train_labels, valtest_labels = split_data(self.symptoms_data, self.disease_data,
                                                                                   shuffle=True, train_size=.7,
                                                                                   test_size=.3)
        self.valid, self.test, self.valid_labels, self.test_labels = split_data(valtest, valtest_labels,
                                                                                              shuffle=True,
                                                                                              train_size=.5,
                                                                                              test_size=.5)

    def get_data_insight(self):
        """
        Prints out useful information about the data.
        """
        print("Symptom's shape:", self.symptoms_data.shape)
        print("Disease's shape:", self.disease_data.shape)
        print('Symptoms at index 0:\n', self.symptoms_data[0])
        print('Disease at index 0:\n', self.disease_data[0])
        
if __name__=='__main__':
    data = SymptomDiseaseData()
    data.generate_data()
    data.get_data_insight()

