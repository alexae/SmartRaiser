from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class running(Resource):
    def get(self):
        status_on_off=StatusOnOff
        # Programm Code hier einfuegen
        #
        #
        return {'isRunning': status_on_off}
    def put(self):
        OnOff = request.form['is_running']
        # Programm Code hier einfuegen
        #
        #
        return {'is_running': OnOff}
api.add_resource(running, '/running')


class humidity(Resource):
    def get(self):
        status_humidity=StatusHumidity
        # Programm Code hier einfuegen
        #
        #
        return {'humidity': status_humidity}
    def put(self):
        val_humidity = request.form['humidity']
        # Programm Code hier einfuegen
        #
        #
        return {'humidity': val_humidity}
api.add_resource(humidity, '/humidity')

class waterlevel(Resource):
    def get(self):
        status_waterlevel=StatusWaterlevel
        # Programm Code hier einfuegen
        #
        #
        return {'waterlevel': status_waterlevel}
api.add_resource(waterlevel, '/waterlevel')

class chargelevel(Resource):
    def get(self):
        status_chargelevel=StatusChargelevel
        # Programm Code hier einfuegen
        #
        #
        return {'chargelevel': status_chargelevel}
api.add_resource(chargelevel, '/chargelevel')
@app.route('/chargelevel' , methods=['GET'])
    
@app.route('/wateringtime' , methods=['GET', 'PUT'])
def wateringtime():
    # Programm Code hier einfuegen
    wateringtime = "00:05"    #String mm:ss /loeschenwenn fertig
    #
    #
    return jsonify(wateringtime)
    
   
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
