import requests


def translate(value):
    """
    :param value:
    :return: the translated values
    """
    if value == 'moderate':
        value = 'en quantité modérée'
    if value == 'high':
        value = 'en quantité élevée'
    if value == 'low':
        value = 'en faible quantité'
    return value


def result_api(code):
    """
    This method is used to make a GET Rest Request
    :param code: get code of product in the database
    :return: return json data
    """
    url_product = "https://fr.openfoodfacts.org/api/v0/produit/{}.json"
    code = int(code)
    data = requests.get(f"{url_product}{code}")
    if data.status_code != 200:
        print("error status_code")
    else:
        result = data.json()['product']
        return result