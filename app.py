from flask import Flask, request
import json
from umd_loss import calc_loss
from umd_globecover import calc_globecover

app = Flask(__name__)

@app.route('/loss', methods=['POST'])
def loss():

    print request.method

    data = json.loads(request.data.decode("utf-8"))
    print data
    
    # when testing locally, need to remove the json.loads() from data['geojson'] for some reason
    output = calc_loss(data['thresh'], json.loads(data['geojson']), data['start'], data['end'])
    print output
    
    return output

@app.route('/globecover', methods=['POST'])
def globecover():

    print request.method

    data = json.loads(request.data.decode("utf-8"))
    print data
    
    # when testing locally, need to remove the json.loads() from data['geojson'] for some reason
    output = calc_globecover(data['thresh'], json.loads(data['geojson']), data['start'], data['end'])
    print output
    
    return output



if __name__ == '__main__':
    app.run()