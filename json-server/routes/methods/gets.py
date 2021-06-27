import json
from flask import Response, request
import re

def slice_docs(docs, keys, query_str):

    range = keys.split('-')

    try:
        if len(range) >= 2:

            if range[0].strip() != '' and range[1].strip() == '':
                docs = docs[int(range[0])::range[2] if len(range) >= 3 else 1]
            
            elif range[0].strip() == '' and range[1].strip() != '':
                docs = docs[:int(range[1]):range[2] if len(range) >= 3 else 1]

            elif range[0].strip() == '' and range[1].strip() == '':
                docs = docs
            
            else:
                docs = docs[int(range[0]):int(range[1]):range[2] if len(range) >= 3 else 1]
        
        elif len(range) == 1:
            docs = docs[int(range[0]):]

        else:
            raise Exception('Slicing operator needs at least one argument.')
    
    except ValueError:
        raise Exception('One of the keys cannot be converted to an integer or no keys were provided! ' + keys)

    except Exception:
        raise Exception('Invalid keys provided! ' + keys)

    return docs 

def sort_docs(docs, keys, query_str):

    order = query_str.get('_order').split(',')[::-1] if query_str.get('_order') else None

    for idx, val in enumerate(keys.split(',')[::-1]):
        try: 
            docs.sort(key=lambda x: x[val], reverse= order[idx] == 'desc' if order and len(order) > idx else False)

        except Exception:
            raise Exception('Sort key was not found: ' + val)

    
    return docs 

def generic_getAll(route, json_file, lock):

    FILTERS = {
        'eq' : lambda e1, e2: e1 == e2,
        'gt' : lambda e1, e2: e1 > e2,
        'lt' : lambda e1, e2: e1 < e2,
        'gte' : lambda e1, e2: e1 >= e2,
        'lte' : lambda e1, e2: e1 <= e2,
        'ne' : lambda e1, e2: e1 != e2
    }

    OPERATIONS = {
        '_sort' : sort_docs,
        '_slice' : slice_docs 
    }

    def func():
        file = open(json_file)

        lock.acquire() 

        result = json.load(file)[route]

        lock.release()

        file.close()

        filters = [arg for arg in request.args if arg[0] != '_'] # Gets all query strings that don't start with '_'.
        operations = [arg for arg in request.args if arg[0] == '_' and arg not in ['_order']] # Gets all query strings that start with '_'.
        
        if operations:
            for op in operations:
                try:
                    result = OPERATIONS[op](result, request.args.get(op), request.args)
                
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


        return Response(json.dumps(result, indent=4),  mimetype='application/json')
    
    return func

def generic_getById(route, json_file, lock):
    def func(id):
        file = open(json_file)

        lock.acquire() 

        data = json.load(file)

        lock.release()

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