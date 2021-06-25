from flask import request, Response
import json

def find_required_fields(l):
    ret = []

    for idx, doc in enumerate(l):
        if idx == 0:
            ret += doc.keys()
        
        ret = list(set(doc.keys()) & set(ret))
    
    return ret

def generic_post(route, json_file, lock):
    def func():
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

        file.close()

        required_fields = find_required_fields(data[route])

        body = request.get_json()

        if body and all([el in body for el in required_fields]):
            with open(json_file, 'w') as j_file:

                data[route].append(body)

                lock.acquire() 
                
                j_file.write(json.dumps(data, indent = 4))

                lock.release()
        
            return Response("Ok", 200)



        return Response('Check if all the required fields are provided in your message: ' + ', '.join(required_fields) + '.',400 , mimetype='application/json')

        
    
    return func


def createPosts(route, json_file, lock):
    routes = []

    # Post a new document to the json. Checks 
    routes.append((f'/{route[0].lower() + route[1:]}', f'post{route.capitalize()}', generic_post(route, json_file, lock), ['POST']))

    return routes