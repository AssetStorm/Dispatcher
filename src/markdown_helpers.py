# -*- coding: utf-8 -*-
from assetstorm_helpers import get_schema, get_types_for_parent, strip_formatting


def clean_list(asset_list: list, allowed_types: list = [],
               schema_cache: dict = {}, schema_id_cache: dict = {}) -> list:
    cleaned_list = []
    for asset in asset_list:
        if asset['type'] in allowed_types:
            cleaned_list.append(collapse_tree(asset, schema_cache=schema_cache, schema_id_cache=schema_id_cache))
        else:
            for key in asset.keys():
                if type(asset[key]) is list:
                    cleaned_list += clean_list(asset_list=asset[key],
                                               allowed_types=allowed_types)
    return cleaned_list


def collapse_tree(tree: dict, schema_cache: dict = {}, schema_id_cache: dict = {}) -> dict:
    schema = schema_cache[tree['type']] if tree['type'] in schema_cache.keys() else \
        get_schema(tree['type'])
    for key in tree.keys():
        if key in ['id', 'type']:
            continue
        if type(tree[key]) is list:
            if type(schema[key]) is list:
                if schema[key][0] == 1:
                    tree[key] = [strip_formatting(x) for x in tree[key]]
                elif schema[key][0] > 3:
                    allowed_types = get_types_for_parent(type_id=schema[key][0])
                    tree[key] = clean_list(tree[key], allowed_types=allowed_types)
            elif schema[key] == 1:
                tree[key] = strip_formatting(tree[key])
        elif schema[key] == 1:
            tree[key] = strip_formatting(tree[key])
    return tree
