from flask import render_template, request, jsonify
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        respone = jsonify({'error': 'not found'})
        respone.status_code = 404
        return respone
    return render_template('404.html', error=e), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        respone = jsonify({'error': 'internal server error'})
        respone.status_code = 500
        return respone
    return render_template('500.html', error=e), 500


@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        respone = jsonify({'error': 'forbidden'})
        respone.status_code = 500
        return respone
    return render_template('404.html', error=e), 403