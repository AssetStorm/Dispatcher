# -*- coding: utf-8 -*-
from typing import Union
from settings import Settings
import requests


class SchemaLoadError(Exception):
    def __init__(self, json_err):
        self.json = json_err


def get_schema(type_name: str = None, type_id: int = None) -> dict:
    if type_id is not None:
        schema_response = requests.get(
            Settings().as_url + "/get_schema?type_id=" + str(type_id))
    else:
        schema_response = requests.get(
            Settings().as_url + "/get_schema?type_name=" + type_name)
    if schema_response.status_code != 200:
        raise SchemaLoadError({
            "Error": "Unable to load the schema of this asset type." +
                     " This was the error:" + schema_response.json()['Error']})
    article_schema = schema_response.json()
    return article_schema


def get_types_for_parent(type_name: str = None, type_id: int = None) -> list:
    if type_id is not None:
        parent_list_response = requests.get(
            Settings().as_url + "/get_types_for_parent?parent_type_id=" + str(type_id))
    else:
        parent_list_response = requests.get(
            Settings().as_url + "/get_types_for_parent?parent_type_name=" + type_name)
    if parent_list_response.status_code != 200:
        raise SchemaLoadError({
            "Error": "Unable to load the list of parents for this asset type." +
                     " This was the error:" + parent_list_response.json()['Error']})
    parent_type_name_list = parent_list_response.json()
    return parent_type_name_list


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
