from flask import Flask, url_for
from markupsafe import escape
from flask import jsonify

app = Flask(__name__)


@app.route('/running' , methods=['GET', 'PUT'])
def running():
    return 'OnOff'

@app.route('/humidity' , methods=['GET', 'PUT'])
def humidity():
    return 'humidity'

@app.route('/user/<username>' , methods=['GET', 'PUT'])
def profile(username):
    return '{}\'s profile'.format(escape(username))

    
if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0")
