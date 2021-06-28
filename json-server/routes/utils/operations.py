def slice_docs(docs, keys, query_str, db):

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

def sort_docs(docs, keys, query_str, db):

    order = query_str.get('_order').split(',')[::-1] if query_str.get('_order') else None

    for idx, val in enumerate(keys.split(',')[::-1]):
        try: 
            docs.sort(key=lambda x: x[val], reverse= order[idx] == 'desc' if order and len(order) > idx else False)

        except Exception:
            raise Exception('Sort key was not found: ' + val)

    
    return docs 


def find_doc(id, records):

    for record in records:
        if 'id' in record and record['id'] == id:
            return record

    return id

def expand_docs(docs, keys, query_str, db):

    expansion = keys.split(':')
    ret = []

    try:
        if expansion[1] not in db:
            raise Exception(f'The target collection {expansion[1]} does not exist on your json file!')

        for doc in docs:
            if expansion[0] in doc:
                doc[expansion[0]] = find_doc(doc[expansion[0]], db[expansion[1]])
    
    except IndexError:
        raise Exception('Syntax error: <record_field>:<target_collection> expected. Provided: ' + keys)
    
    except Exception as e:
        raise e

    return docs