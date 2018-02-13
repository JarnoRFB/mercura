
# coding: utf-8

# In[11]:

import numpy as np
import pandas as pd
import pickle as pk

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

    def generate_data(self):
        """
        Puts symptoms and diseases in numpy arrays
        Returns:
            weekly_symptoms, weekly_diseases-->numpy arrays
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
        return self.symptoms_data, self.disease_data

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

