from methods.gets import createGets
from methods.posts import createPosts
from methods.puts import createPuts
from methods.deletes import createDeletes

def routesCreator(app, json_data):

    for route in json_data:
        createGets(app, route)
        createPosts(app, route)
        createPuts(app, route)
        createDeletes(app, route)
