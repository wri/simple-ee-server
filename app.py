from flask import Flask, request
import json
from umd import calc_loss

app = Flask(__name__)


@app.route('/', methods=['POST'])
def run():

    print request.method

    data = json.loads(request.data.decode("utf-8"))
    print data
    
    output = calc_loss(data['thresh'], json.loads(data['geojson']), data['start'], data['end'])
    print output
    
    return output



if __name__ == '__main__':
    app.run()