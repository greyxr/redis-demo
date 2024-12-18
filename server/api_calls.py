import requests

baseUrl = 'https://api.guildwars2.com/v2'
skinsUrl = baseUrl + '/skins'
accountSkinsUrl = baseUrl + '/account/skins'
pageSize = 200
api_key = 'api_key_here'

def paginatedLoad(url, auth=None):
    itemArray = []
    i = 0
    while True:
        params = {
            "page": i,
            "page_size": pageSize
            }
        if (auth is not None):
            params["access_token"] = auth
        response = requests.get(url, params=params)
        items = response.json()
        if (len(items) == 0 or len(items) == 1):
            break
        itemArray.extend(items)
        i += 1
    return itemArray

def singleLoad(url, auth=None):
    params = {
        }
    if (auth is not None):
        params["access_token"] = auth
    response = requests.get(url, params=params)
    return response.json()