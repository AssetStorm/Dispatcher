# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from typing import Union
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
