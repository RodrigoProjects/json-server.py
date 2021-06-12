import sys
import json
import flask
from routes.handler import routesCreator


def main(args):

    port = 3500 # Default port.

    if len(args) >= 2: 
        with open(args[1]) as json_file:
            json_data = json.load(json_file)

            if type(json_data) is not dict:
                print('The json file needs to start with an object {} and not a list or any other type.')
                exit()

    if len(args) >= 3: 
        try:
            port = int(args[2])

        except Exception as e:
            print('ERROR: The second argument of json-server needs to be an integer.\nExample: json-server.py <json_file> <port>')
            exit()

    
    app = flask.Flask(__name__)

    routesCreator(app, json_data)
    
    app.run(debug=True, port=port)



if __name__ == '__main__':
    main(sys.argv)