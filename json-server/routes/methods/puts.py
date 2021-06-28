from flask import Response, request
import json

def generic_put(route, json_file, lock):
    def func(id):
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

        file.close()
        
        if type(data[route]) is dict:
            data[route] = [data[route]]

        aux = []
        edited = False 

        body = request.get_json()

        for doc in data[route]:
            if edited or id not in [str(el) for el in doc.values()]:
                aux.append(doc)

            else:
                for k in body:
                    doc[k] = body[k]
                
                aux.append(doc)
                edited = True
        
        if not edited:
            return Response('Nothing was updated!', 202 , mimetype='application/json')

        data[route] = aux

        with open(json_file, 'w') as j_file:

                lock.acquire() 
                
                j_file.write(json.dumps(data, indent = 4))

                lock.release()

        return Response('Ok', 200 , mimetype='application/json')

        
    
    return func


def createPuts(route, json_file, lock):
    routes = []

    # Deletes a document from the db. Needs the id of the document passed by params.
    routes.append((f'/{route[0].lower() + route[1:]}/<id>', f'put{route.capitalize()}', generic_put(route, json_file, lock), ['PUT', 'PATCH']))

    return routes