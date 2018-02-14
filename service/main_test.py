import requests

data = {'symptoms': {
    'Ausschlag an Haut oder Schleimhaut mit Flecken, Bläschen oder Pusteln (außer Herpes zoster)': 5,
    'Ausschlag an Haut oder Schleimhaut mit gleichzeitig vorhandenen Papeln, Bläschen bzw. Pusteln und Schorf (sog. Sternenhimmel)': 3,
    'Ausschlag, einseitig auf Hautsegment beschränkt, bläschenförmig': 7,
    'Brennen, Juckreiz': 9,
    'Durchfall und/oder Erbrechen': 4,
    'Durchfall, nicht näher bezeichnet': 0,
    'Fetales (kongenitales) Varizellensyndrom': 2,
    'Fieber': 12,
    'Gliederschmerzen': 4,
    'Husten': 8,
    'Muskel-, Glieder-, Rücken- oder Kopfschmerzen': 2,
    'Pneumonie (Lungenentzündung)': 0,
    'Schmerzen im betroffenen Bereich (Zosterneuralgie)': 3,
    'Schmerzen, einseitig auf ein Hautsegment lokalisiert, ohne Ausschlag': 1,
    'akuter Krankheitsbeginn': 2,
    'akutes schweres Atemnotsyndrom (ARDS)': 0,
    'andere Symptome': 9,
    'beatmungspflichtige Atemwegserkrankung': 0}

}

test1 = requests.post('http://127.0.0.1:8080/webhook', json=data)
print(test1.json())
