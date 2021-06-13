from .methods.gets import createGets
import json


def routesCreator(app, json_routes, json_file, lock):
    routes = []
    file = open(json_file)

    for route in json_routes:
        
        aux = createGets(route, json_file, lock)
        
        routes += aux
    
    file.close()

    for route, func_name, func, methods in routes:
        app.add_url_rule(
            route,
            func_name,
            methods = methods
        )

        app.view_functions[func_name] = func