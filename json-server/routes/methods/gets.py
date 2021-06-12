import json
from flask import Response

def generic_getAll(route, json_file, lock):
    def func():
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

        file.close()

        return Response(json.dumps(data[route]),  mimetype='application/json')
    
    return func


def createGets(route, json_file, lock):
    routes = []

    # Get all elements for a specific json key.
    routes.append((f'/{route[0].lower() + route[1:]}', f'get{route.capitalize()}', generic_getAll(route, json_file, lock), ['GET']))

    return routes