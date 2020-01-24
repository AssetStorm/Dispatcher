# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from response_helpers import build_text_response, build_json_response
from settings import Settings
import requests
import yaml
import os
app = Flask(__name__)


@app.route("/convert/markdown/<string:target_format>", methods=['POST'])
def convert(target_format: str) -> Response:
    md_str = request.get_data(as_text=True)
    md_converter_response = requests.post(
        Settings().md_conv_url + "/",
        data=md_str)
    as_tree = md_converter_response.json()
    if md_converter_response.status_code != 200 or 'type' not in as_tree:
        if 'Error' in as_tree:
            return build_json_response(app, as_tree, status=400)
        return build_json_response(
            app, {"Error": "An error occurred while converting the markdown document."},
            status=400)
    if len(as_tree['conversion_container']['blocks']) < 1:
        return build_json_response(
            app, {"Error": "The document was empty."},
            status=400)
    if len(as_tree['conversion_container']['blocks']) > 1:
        return build_json_response(
            app, {"Error": "The document must contain exactly one article. Did you forget the header?"},
            status=400)
    article = as_tree['conversion_container']['blocks'][0]
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
    if md_converter_response.status_code != 200:
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
    # found:
    #   load the article, and search for images and other blobs like video; compare the hashes
    #     for all identical hashes insert the existing asset id
    #   insert the id of the article in the tree
    # for all unidentified blobs in the new tree load them to the blob storage and insert urls and hashes
    # save the article in AssetStorm
    # reload the saved article from AssetStorm
    # send the loaded article to the templater and return the result
    return build_text_response(app, "<div>foo</div>", mime_type='text/html')


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
