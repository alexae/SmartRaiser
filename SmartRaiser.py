from flask import Flask
from markupsafe import escape
from flask import jsonify

app = Flask(__name__)
#Statische Werte zum Testen der API -> Löschen nach ferigstellung
OnOff = True            #boolean
humidity = 40           #Int
waterlevel = 0          #int
chargelevel = 0         #Int
wateringtime = 00:05    #String mm:ss

# Bis hier löschen

@app.route('/running', methods=['GET', 'PUT'])
def running():
    # Programm Code hier einfügen
    #
    #
    return OnOff

@app.route('/humidity' , methods=['GET', 'PUT'])
def humidity():
    # Programm Code hier einfügen
    #
    #
    return humidity

@app.route('/waterlevel' , methods=['GET'])
def waterlevel():
    # Programm Code hier einfügen
    #
    #
    return waterlevel
    
@app.route('/chargelevel' , methods='GET')
def chargelevel():
    # Programm Code hier einfügen
    #
    #
    return chargelevel
    
@app.route('/wateringtime' , methods='GET', 'PUT')
def wateringtime():
    # Programm Code hier einfügen
    #
    #
    return wateringtime
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
