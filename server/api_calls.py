import requests

baseUrl = 'https://api.guildwars2.com/v2'
skinsUrl = baseUrl + '/skins'
accountSkinsUrl = baseUrl + '/account/skins'
pageSize = 200
api_key = 'C5A11C84-AE63-DC4F-94B3-F8BAB29A1990D798571D-982B-409A-813A-A220C218A7E9'

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