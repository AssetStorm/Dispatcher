# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from response_helpers import build_text_response, build_json_response, get_mime_type
from hash_helpers import hash_file
from assetstorm_helpers import strip_formatting
from settings import Settings
import requests
import yaml
import json
import os
app = Flask(__name__)


@app.route("/convert/markdown/<string:target_format>", methods=['POST'])
def convert_markdown(target_format: str) -> Response:
    article_filename = None
    for filename in request.files:
        if filename.endswith('.md'):
            article_filename = filename
            break
    for filename in request.files:
        if filename.endswith('.txt'):
            article_filename = filename
            break
    if article_filename is None:
        return build_json_response(
            app, {"Error": "There was no .md or .txt file in the upload."},
            status=400)
    binary_files = []
    for filename in request.files:
        if filename != article_filename:
            binary_files.append({
                "filename": filename,
                "hash": hash_file(request.files[filename])
            })
    try:
        md_str = str(request.files[article_filename].read(), encoding='utf-8')
    except UnicodeDecodeError:
        return build_json_response(
            app, {"Error": "The uploaded markdown was not encoded as UTF-8."},
            status=400)
    md_converter_response = requests.post(
        Settings().md_conv_url + "/",
        data=md_str.encode('utf-8'))
    md_converter_response.encoding = 'utf-8'
    try:
        as_tree = md_converter_response.json()
    except json.JSONDecodeError as e:
        return build_json_response(
            app, {"Error": "The markdown converter did not return JSON. This was the JSONDecodeError: " + str(e)},
            status=400)
    if md_converter_response.status_code != 200 or \
            'type' not in as_tree or 'blocks' not in as_tree or \
            'conversion-container' not in as_tree['type']:
        if 'Error' in as_tree:
            return build_json_response(app, as_tree, status=400)
        return build_json_response(
            app, {"Error": "An error {} occurred while converting the markdown document: {}".format(
                md_converter_response.status_code,
                md_converter_response.text)},
            status=400)
    if len(as_tree['blocks']) < 1:
        return build_json_response(
            app, {"Error": "The document was empty."},
            status=400)
    if len(as_tree['blocks']) > 1:
        return build_json_response(
            app, {"Error": "The document must contain exactly one article. Did you forget the header?"},
            status=400)
    article = as_tree['blocks'][0]
    schema_response = requests.get(
        Settings().as_url + "/get_schema?type_name=" + article['type'])
    if schema_response.status_code != 200:
        return build_json_response(
            app, {"Error": "Unable to load the schema of this article type." +
                           " This was the error:" + schema_response.json()['Error']},
            status=400)
    article_schema = schema_response.json()
    for key in article_schema.keys():
        if article_schema[key] == 1:
            article[key] = strip_formatting(article[key])
    return convert_asset_storm(target_format, article)


def convert_asset_storm(target_format: str, article: dict) -> Response:
    if 'type' not in article:
        return build_json_response(
            app, {"Error": "The document did not define an article type. Please add a \"type\" key."},
            status=400)
    if 'x_id' not in article:
        return build_json_response(
            app, {"Error": "The document did not reference an x_id. Please add a \"x_id\" key."},
            status=400)
    article_list_response = requests.get(
        Settings().as_url + "/get_types_for_parent?parent_type_name=article")
    if article_list_response.status_code != 200:
        return build_json_response(
            app, {"Error": "Unable to load list of article types."},
            status=400)
    article_type_list = article_list_response.json()
    if article['type'] not in article_type_list:
        return build_json_response(
            app, {"Error": "Unknown article type: {}. Valid types are: {}".format(
                article['type'], str(article_type_list))},
            status=400)
    # query AssetStorm for an article with this xp_id
    article_query_response = requests.get(
        Settings().as_url + "/find",
        json={"x_id": article['x_id']},
        headers={'Content-Type': 'application/json'})
    found_assets = article_query_response.json()['assets']
    if len(found_assets) >= 1:
        # found:
        #   load the article, and search for images and other blobs like video; compare the hashes
        #     for all identical hashes insert the existing asset id
        loaded_article_response = requests.get(Settings().as_url + "/find?id=" + found_assets[0]['id'])
        print(loaded_article_response.text)
        #   insert the id of the article in the tree
        loaded_article = loaded_article_response.json()
        article['id'] = loaded_article['id']
    # for all unidentified blobs in the new tree load them to the blob storage and insert urls and hashes
    # save the article in AssetStorm
    article_save_response = requests.post(
        Settings().as_url + "/save",
        json=article,
        headers={'Content-Type': 'application/json'})
    if article_save_response.status_code != 200:
        return build_json_response(
            app, article_save_response.json(),
            status=400)
    new_id = article_save_response.json()['id']
    # reload the saved article from AssetStorm
    loaded_article_response = requests.get(Settings().as_url + "/load?id=" + new_id)
    if loaded_article_response.status_code != 200:
        return build_json_response(
            app, loaded_article_response.json(),
            status=400)
    article = loaded_article_response.json()
    # send the loaded article to the templater and return the result
    templater_response = requests.post(
        Settings().templater_url + "/",
        json={
            "assetstorm_url": Settings().intern_as_url,
            "template_type": target_format,
            "tree": article
        }, headers={'Content-Type': 'application/json'})
    if templater_response.status_code != 200:
        return build_json_response(
            app, templater_response.json(),
            status=400)
    return build_text_response(app, templater_response.text, mime_type=get_mime_type(target_format))


@app.route("/convert/assetstorm/<string:target_format>", methods=['POST'])
def convert_asset_storm_post(target_format: str) -> Response:
    return convert_asset_storm(target_format, request.json)


@app.route("/openapi.json", methods=['GET'])
def open_api_definition() -> Response:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           "DispatcherAPI.yaml"), 'r') as yaml_file:
        api_definition = yaml.safe_load(yaml_file.read())
    if os.getenv("SERVER_NAME") is not None:
        api_definition["servers"][0]['url'] = os.getenv("SERVER_NAME")
    return build_json_response(app, api_definition)


@app.route("/live", methods=['GET'])
def live():
    try:
        converter_response = requests.get(Settings().md_conv_url + "/live")
    except requests.ConnectionError:
        return build_json_response(
            app, {"Error": "The url {} is unreachable.".format(Settings().md_conv_url + "/live")},
            status=400)
    if converter_response.status_code != 200:
        return build_json_response(
            app, converter_response.json(), status=400)
    return build_text_response(app, "", status=200)


if __name__ == "__main__":  # pragma: no mutate
    app.run()  # pragma: no cover
