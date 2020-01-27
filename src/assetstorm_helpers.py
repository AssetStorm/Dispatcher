# -*- coding: utf-8 -*-
from typing import Union
from settings import Settings
import requests


def strip_formatting(tree: Union[dict, list, str, int]) -> Union[str, int]:
    def render_with_templater(tree_for_templating: dict) -> str:
        response = requests.post(
            Settings().templater_url + "/",
            json={
                "assetstorm_url": Settings().intern_as_url,
                "template_type": "raw",
                "tree": tree_for_templating
            }, headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            print(response.text)
            raise ConnectionError(response.json()['Error'])
        return response.text

    if type(tree) is str:
        return tree
    if type(tree) is int:
        return str(tree)
    if type(tree) is dict:
        return render_with_templater(tree).strip()
    if type(tree) is list:
        return " ".join([render_with_templater(item).strip() for item in tree])
    raise TypeError("tree must be dict, list, str or int. It is {} with content {}.".format(type(tree), tree))
