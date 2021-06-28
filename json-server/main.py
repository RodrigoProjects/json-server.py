#!/usr/bin/python3
import sys
import json
import flask
from flask import render_template
import threading
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

    mainLock = threading.Lock() # Will assure thread safe reads and writes in files.

    # args[1] is the json file.

    # Index documentation of the json-server.py generated.
    app.add_url_rule(
            '/',
            'index',
            methods = ['GET']
        )

    app.view_functions['index'] = default_route(args[1], mainLock)

    # ----------------------------------------------------------

    routesCreator(app, json_data.keys(), args[1] , mainLock)
    
    app.run(debug=True, port=port)


def default_route(filename, lock):
    def func():
        file = open(filename)

        lock.acquire() 

        result = json.load(file)

        lock.release()

        file.close()

        return render_template("index.html",data = result)

    return func

if __name__ == '__main__':
    main(sys.argv)