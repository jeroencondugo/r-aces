#  Copyright (c) 2015-2020 Condugo bvba

from flask import g, jsonify, request
from datetime import datetime


def make_response(schema, response, message, warning_msg=None, error_msg=None, pagination=None, status_code=200):
    user = g.user.email if hasattr(g.user, 'email') else 'anonymous'

    params = {
        'params': request.args.to_dict(),
        'user': user,
        'message': message,
        'response': response,
        'time': datetime.utcnow(),
    }

    if warning_msg:
        params['warning'] = warning_msg
    if error_msg:
        params['error'] = error_msg
    if pagination:
        params['pagination'] = pagination

    if schema:
        resp = jsonify(schema.dump(params).data)
    else:
        resp = jsonify(params)

    resp.status_code = status_code

    return resp
