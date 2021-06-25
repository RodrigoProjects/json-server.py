from .methods.gets import createGets
from .methods.posts import createPosts
from .methods.deletes import createDeletes
from .methods.puts import createPuts
import json



def routesCreator(app, json_routes, json_file, lock):
    routes = []
    file = open(json_file)

    for route in json_routes:
        
        aux = createGets(route, json_file, lock) + createPosts(route, json_file, lock) + createDeletes(route, json_file, lock) + createPuts(route, json_file, lock)
        
        routes += aux
    
    file.close()

    for route, func_name, func, methods in routes:
        app.add_url_rule(
            route,
            func_name,
            methods = methods
        )

        app.view_functions[func_name] = func