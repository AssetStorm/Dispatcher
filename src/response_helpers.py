# -*- coding: utf-8 -*-
from dispatcher import app
from flask import Response
from typing import Union
import json


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
