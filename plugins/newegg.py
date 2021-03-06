from util import hook, http, text, web
import json
import requests
import re
## CONSTANTS

ITEM_URL = "http://www.newegg.com/Product/Product.aspx?Item={}"

API_PRODUCT = "http://www.ows.newegg.com/Products.egg/{}/ProductDetails"
API_SEARCH = "http://www.ows.newegg.com/Search.egg/Advanced"

NEWEGG_RE = (r"(?:(?:www.newegg.com|newegg.com)/Product/Product\.aspx\?Item=)([-_a-zA-Z0-9]+)", re.I)


## OTHER FUNCTIONS

def format_item(item, show_url=True):
    """ takes a newegg API item object and returns a description """
    title = text.truncate_str(item["Title"], 50)

    # format the rating nicely if it exists
    if not item["ReviewSummary"]["TotalReviews"] == "[]":
        rating = "Rated {}/5 ({} ratings)".format(item["ReviewSummary"]["Rating"],
                                                          item["ReviewSummary"]["TotalReviews"][1:-1])
    else:
        rating = "No Ratings"

    if not item["FinalPrice"] ==  item["OriginalPrice"]:
        price = "{FinalPrice}, was {OriginalPrice}".format(**item)
    else:
        price = item["FinalPrice"]

    tags = []

    if item["Instock"]:
        tags.append("\x02Stock Available\x02")
    else:
        tags.append("\x02Out Of Stock\x02")

    if item["FreeShippingFlag"]:
        tags.append("\x02Free Shipping\x02")

    if item["IsFeaturedItem"]:
        tags.append("\x02Featured\x02")

    if item["IsShellShockerItem"]:
        tags.append("\x02SHELL SHOCKER®\x02")

    # join all the tags together in a comma seperated string ("tag1, tag2, tag3")
    tag_text = u", ".join(tags)

    if show_url:
        # create the item URL and shorten it
        url = web.try_isgd(ITEM_URL.format(item["NeweggItemNumber"]))
        return u"\x02{}\x02 ({}) - {} - {} - {}".format(title, price, rating,
                                                    tag_text, url)
    else:
        return u"\x02{}\x02 ({}) - {} - {}".format(title, price, rating,
                                                tag_text)


## HOOK FUNCTIONS

@hook.regex(*NEWEGG_RE)
def newegg_url(match):
    item_id = match.group(1)
	
    # newegg ur hurting my feelings
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) '
                      'Version/5.1 Mobile/9A334 Safari/7534.48.3',
        'Referer': 'http://www.newegg.com/'
    }

    item = requests.get(API_PRODUCT.format(item_id), headers=headers).json()
    return format_item(item, show_url=False)



@hook.command
def newegg(inp):
    """newegg <item name> -- Searches newegg.com for <item name>"""

    # form the search request
    request = {
        "Keyword": inp,
        "Sort": "FEATURED"
    }
    # i need to lie to apis now too?
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) '
                      'Version/5.1 Mobile/9A334 Safari/7534.48.3',
        'Referer': 'http://www.newegg.com/'
    }
    # submit the search request
    try:
        request = requests.post(
            'http://www.ows.newegg.com/Search.egg/Advanced',
            data=json.dumps(request).encode('utf-8'),
            headers=headers
        )
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Unable to find product: {}".format(e)

    r = request.json()

    if r.get("Description", False):
        return "Newegg Error: {Description} (\x02{Code}\x02)". format(**r)

    # get the first result
    if r["ProductListItems"]:
        return format_item(r["ProductListItems"][0])
    else:
        return "No results found."

