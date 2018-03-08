import requests

data = {'queryResult': 
            {'action': 'prevention.information.schmierinfektion3',
            'parameters': {
                'disease': 'Noro-Gastroenteritis'
            },
            'outputContexts': ''}
        }
         

test1 = requests.post('http://127.0.0.1:8080/webhook', json=data)
print(test1.json())
