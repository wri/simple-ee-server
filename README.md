# simple-ee-server

This is a flask-based GEE server that can be run with Gunicorn to test response time for simultaneous requests. Most useful when testing something developed in the [GEE playground](https://code.earthengine.google.com) to see how it responds in a production-like environment.

### Linux Deployment

1. sudo pip install -r requirements.txt
2. earthengine authenticate
3. sudo gunicorn -b 0.0.0.0:80 app:app -w 10

(The above runs the application on port 80 with 10 workers. Must be in the simple-ee-server directory, so that app.py is visible).


### Windows testing environment

Gunicorn doesn't run on Windows, but running `python app.py` should start a single threaded application at `localhost:5000`. This can be used to test the endpoints and GEE code before deploying on a Linux machine.
