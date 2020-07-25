#Bibliotheken einbinden
from flask import Flask, jsonify, request
import shelve
import time
import datetime
import dbm
import json
import RPi.GPIO as GPIO
from MCP3008 import MCP3008   #SPI_API

#GPIO Modus (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#GPIO Pins zuweisen
#Echo Komunikation
GPIO_TRIGGER = 3
GPIO_ECHO = 4
#Richtung der GPIO-Pins festlegen (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
#Batterie Ladestand
GPIO.setup(17, GPIO.IN) #Batterie tief
GPIO.setup(27, GPIO.IN) #Batterie 50%
GPIO.setup(22, GPIO.IN) #Batterie Ok
# Pumpe
GPIO.setup(21, GPIO.OUT) #Ansteuerung des MOSFET für den Motor

app = Flask(__name__)



@app.route('/')
def index():
    watering()
    return 'SmartRaiser is running!'


@app.route('/humidity')
def handle_humidity():
    # Read current humidity from sensor
    adc = MCP3008()
    value = adc.read( channel = 1 ) # Den auszulesenden Channel kannst du natürlich anpassen
    humidity=value / 1023.0 * 3.3
    print(humidity)
    return jsonify(
        humidity
    )

@app.route('/waterlevel')
def handle_waterlevel():
    # Read current water level from sensor
    # setze Trigger auf HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # setze Trigger nach 0.01ms aus LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartZeit = time.time()
    StopZeit = time.time()

    # speichere Startzeit
    while GPIO.input(GPIO_ECHO) == 0:
        StartZeit = time.time()

    # speichere Ankunftszeit
    while GPIO.input(GPIO_ECHO) == 1:
        StopZeit = time.time()

    # Zeit Differenz zwischen Start und Ankunft
    TimeElapsed = StopZeit - StartZeit
    # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
    # und durch 2 teilen, da hin und zurueck
    distanz = (TimeElapsed * 34300) / 2
    return jsonify(
        waterlevel=distanz
    )
   
@app.route('/chargelevel')
def handle_chargelevel():
    # Read current charge level from sensor
    if GPIO.input(17) == GPIO.HIGH:
        chargelevel=0
    if GPIO.input(27) == GPIO.HIGH:
        chargelevel=50
    if GPIO.input(22) == GPIO.HIGH:
        chargelevel=100
    return jsonify(
        chargelevel
    )


@app.route('/humiditytoachieve', methods=['GET', 'PUT'])
def handle_humidity_to_achieve():
    if request.method == 'PUT':
        content = request.json
        humidity = content['humidity']

        data = shelve.open('humidity')
        data['humidity'] = humidity
        data.close()

        return jsonify({"humidity": humidity})

    elif request.method == 'GET':
        data = shelve.open('humidity')

        if 'humidity' in data:
            return jsonify(
                humidity=data['humidity']
            )
        else:
            return "", 204

        data.close()


@app.route('/wateringtimes', methods=['GET', 'PUT'])
def handle_wateringtimes():
    if request.method == 'PUT':
        content = request.json
        wateringtimes = content['wateringtimes']

        data = shelve.open('wateringtimes')
        data['wateringtimes'] = wateringtimes
        data.close()

        return jsonify({
            "wateringtimes": wateringtimes
        })

    elif request.method == 'GET':

        data = shelve.open('wateringtimes')

        if 'wateringtimes' in data:
            print(data['wateringtimes'])
            return jsonify(
                wateringtimes=data['wateringtimes']
            )
            json.loads(wateringtimes)
        else:
            return "", 204

        data.close()
def watering():
    #Bestimmen der Statischen Parameter
    #Waeserungsdauer und Messdauer in min (umrechnung in ms)
    wateringduration = 3 # * 60 *1000 Umrechnung in Minuten
    messuringtime = 5 # * 60 * 1000 Umrechnung in Minuten

    data = shelve.open('wateringtimes')
    #Auslesen der Bewässerungszeit
    if 'wateringtimes' in data:
        WT=data['wateringtimes']
        data.close()
    #Auslesen der aktuellen Zeit
        timenow =(datetime.datetime.now().strftime("%H:%M"))

    #Bewässerungslogik
        wateringfrom = (WT["from"])
        wateringto = (WT["to"])
    if timenow >= wateringfrom and timenow <= wateringto:
        for i in range(wateringduration):
            GPIO.output(21, GPIO.HIGH)
            time.sleep(0.001)
            print(i)
        for i in range(messuringtime):
            GPIO.output(21, GPIO.LOW)
            time.sleep(0.001)
            print("Messung läuft")
    else:
        GPIO.output(21, GPIO.LOW)
        print("Bewässern nicht erwünscht")
        print(timenow)
        print("Eingestellte Bewaesserungszeiten von", WT)
    

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
    
