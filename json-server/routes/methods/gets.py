import json
from flask import Response, request # Flask response Object and request for body parsing.
import re # Regex
from ..utils.operations import * # Filter and Operations imported

# ------------- POSSIBLE FILTERS -------------
FILTERS = {
    'eq' : lambda e1, e2: e1 == e2,
    'gt' : lambda e1, e2: e1 > e2,
    'lt' : lambda e1, e2: e1 < e2,
    'gte' : lambda e1, e2: e1 >= e2,
    'lte' : lambda e1, e2: e1 <= e2,
    'ne' : lambda e1, e2: e1 != e2
}
# --------------------------------------------
# ------------- POSSIBLE OPERATIONS ----------
OPERATIONS = {
    '_sort' : sort_docs,
    '_slice' : slice_docs,
    '_expand' : expand_docs
}
# --------------------------------------------

def generic_getAll(route, json_file, lock):

    def func():
        isDict = False 

        file = open(json_file)

        lock.acquire() 

        data = json.load(file)
        result = data[route]

        lock.release()

        if type(result) is dict:
            result = [result]
            isDict = True

        file.close()

        filters = [arg for arg in request.args if arg[0] != '_'] # Gets all query strings that don't start with '_'.
        operations = [arg for arg in request.args if arg[0] == '_' and arg not in ['_order']] # Gets all query strings that start with '_'.
        
        if operations:
            for op in operations:
                try:
                    result = OPERATIONS[op](result, request.args.get(op), request.args, data)

                except Exception as e:
                    return Response(repr(e), 400, mimetype='application/json')

        if filters: # If we have filters in the query string.
            filtered = []

            for doc in result: # We try do find a doc in the json file that isValid for all filters.
                isValid = []

                for filter in filters:

                    # Match _gt, _eq, etc... Filters.
                    if any(filter.endswith(el) for el in ['_' + el for el in FILTERS.keys()]):
                        field = '_'.join(filter.split('_')[:-1])
                        operation = filter.split('_')[-1]

                        if '.' in field:
                            splited = field.split('.')
                            if splited[0] in doc and splited[1] in doc[splited[0]]:
                                field_value = doc[splited[0]][splited[1]]
                            else:
                                isValid.append(False)
                                continue
                        else:

                            if field in doc:
                                print(doc[field])
                                field_value = doc[field]
                            else:
                                isValid.append(False)
                                continue

                        
                        try:
                            val = int(request.args.get(filter))
                            isValid.append(FILTERS[operation](field_value, val))

                        except ValueError:
                            isValid.append(FILTERS[operation](field_value, request.args.get(filter)))
                    
                    # Match simple filters.
                    else:
                        
                        if '.' in filter:

                            splited = filter.split('.')

                            if splited[0] in doc and splited[1] in doc[splited[0]]:
                                isValid.append(request.args.get(filter) in str(doc[splited[0]][splited[1]]))
                            else:
                                isValid.append(False)

                        else:    
                            isValid.append(request.args.get(filter) in str(doc[filter])) if filter in doc else isValid.append(False)
                
                if all(isValid):
                    filtered.append(doc)

            result = filtered

        if isDict:
            return Response(json.dumps(result[0] if len(result) == 1 else result, indent=4),  mimetype='application/json')

        return Response(json.dumps(result, indent=4),  mimetype='application/json')
    
    return func

def generic_getById(route, json_file, lock):

    def func(id):
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

        if type(data[route]) is dict:
            data[route] = [data[route]]
        
        operations = [arg for arg in request.args if arg[0] == '_' and arg not in ['_order']] # Gets all query strings that start with '_'.

        if operations:
            for op in operations:
                try:
                    data[route] = OPERATIONS[op](data[route], request.args.get(op), request.args, data)

                except Exception as e:
                    return Response(repr(e), 400, mimetype='application/json')

        for doc in data[route]:
            for key in doc:
                if str(doc[key]) == id:
                    return Response(json.dumps(doc, indent=4),  mimetype='application/json')
        

        file.close()


        return Response(json.dumps({}),  mimetype='application/json')

        
    
    return func


def createGets(route, json_file, lock):
    routes = []

    # Get all elements for a specific model. These elements can be filtered and transformed.
    routes.append((f'/{route[0].lower() + route[1:]}', f'get{route.capitalize()}', generic_getAll(route, json_file, lock), ['GET']))

    # Get element by uid.
    routes.append((f'/{route[0].lower() + route[1:]}/<id>', f'get{route.capitalize()}ById', generic_getById(route, json_file, lock), ['GET']))

    return routes