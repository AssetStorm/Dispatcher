# -*- coding: utf-8 -*-
from flask import Flask, Response
from typing import Union
import json


def get_mime_type(target_format: str) -> str:
    if target_format == 'markdown':
        return 'text/markdown'
    if target_format in ['proof_html']:
        return 'text/html'
    if target_format in ['sy_xml']:
        return 'text/xml'
    return 'text/plain'


def build_json_response(app: Flask, content: Union[dict, list], status: int = 200) -> Response:
    response = app.response_class(
        response=json.dumps(content),
        status=status,
        mimetype='application/json'
    )
    return response


def build_text_response(app: Flask, content: str, status: int = 200, mime_type: str = 'text/plain') -> Response:
    response = app.response_class(
        response=content.encode('utf-8'),
        status=status,
        mimetype=mime_type
    )
    if mime_type.startswith('text'):
        response.headers["Content-Type"] = mime_type + '; charset=utf-8'
    return response
