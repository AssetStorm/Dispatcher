# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from typing import Union
import requests
import json
import yaml
import os
app = Flask(__name__)


def build_json_response(content: Union[dict, list], status: int = 200) -> Response:
    response = app.response_class(
        response=json.dumps(content),
        status=status,
        mimetype='application/json'
    )
    return response


def build_text_response(content: str, status: int = 200, mime_type: str = 'text/plain') -> Response:
    response = app.response_class(
        response=content,
        status=status,
        mimetype=mime_type
    )
    return response


@app.route("/convert/markdown/<string:target_format>", methods=['POST'])
def convert(target_format: str) -> Response:
    md_str = request.get_data(as_text=True)
    md_converter_response = requests.post(
        os.getenv("MARKDOWN2ASSETSTORM_URL", "https://markdown2assetstorm.assetstorm.pinae.net") + "/",
        data=md_str)
    as_tree = md_converter_response.json()
    if md_converter_response.status_code != 200 or 'type' not in as_tree:
        if 'Error' in as_tree:
            return build_json_response(as_tree, status=400)
        return build_json_response({"Error": "An error occured while converting the markdown document."}, status=400)
    # query AssetStorm for an article with this xp_id
    # found:
    #   load the article, and search for images and other blobs like video; compare the hashes
    #     for all identical hashes insert the existing asset id
    #   insert the id of the article in the tree
    # for all unidentified blobs in the new tree load them to the blob storage and insert urls and hashes
    # save the article in AssetStorm
    # reload the saved article from AssetStorm
    # send the loaded article to the templater and return the result
    return build_text_response("<div>foo</div>", mime_type='text/html')


@app.route("/openapi.json", methods=['GET'])
def open_api_definition() -> Response:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           "DispatcherAPI.yaml"), 'r') as yaml_file:
        api_definition = yaml.safe_load(yaml_file.read())
    if os.getenv("SERVER_NAME") is not None:
        api_definition["servers"][0]['url'] = os.getenv("SERVER_NAME")
    return build_json_response(api_definition)


if __name__ == "__main__":  # pragma: no mutate
    app.run()  # pragma: no cover
