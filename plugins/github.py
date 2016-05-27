import re

from util import hook, http, web

@hook.command("git")
@hook.command
def github_search(inp):
    """git <search query> -- Search github for a specific repo"""
    try:
        data = http.get_json(("https://api.github.com/search/repositories?q=foo&sort=stars&order=desc"), q=inp.strip())
    except Exception as e:
        return "Could not find repo: {}".format(e)
    try:
        reponame = data["items"][0]["full_name"]
        repourl = data["items"][0]["html_url"]
    except IndexError:
        return "Could not find repo"
    return u"\x02{}\x02 - \x02{}\x02".format(reponame, repourl)