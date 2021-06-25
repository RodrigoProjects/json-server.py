from flask import Response
import json

def generic_delete(route, json_file, lock):
    def func(id):
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

        file.close()

        aux = []
        deleted = False 

        for doc in data[route]:
            if deleted or id not in [str(el) for el in doc.values()]:
                aux.append(doc)

            else:
                deleted = True
        
        if data[route] == aux:
            return Response('Nothing was deleted!', 202 , mimetype='application/json')

        data[route] = aux

        with open(json_file, 'w') as j_file:

                lock.acquire() 
                
                j_file.write(json.dumps(data, indent = 4))

                lock.release()

        return Response('Ok', 200 , mimetype='application/json')

        
    
    return func


def createDeletes(route, json_file, lock):
    routes = []

    # Deletes a document from the db. Needs the id of the document passed by params.
    routes.append((f'/{route[0].lower() + route[1:]}/<id>', f'delete{route.capitalize()}', generic_delete(route, json_file, lock), ['DELETE']))

    return routes