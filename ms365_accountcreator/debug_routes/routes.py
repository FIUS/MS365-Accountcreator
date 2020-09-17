"""
Module containing debug routes index page.
"""

from flask import render_template
from .. import APP
from . import debug_blueprint


@debug_blueprint.route('/routes/')
def routes():
    output = []
    for rule in APP.url_map.iter_rules():

        line = {
            'endpoint': rule.endpoint,
            'methods': ', '.join(rule.methods),
            'url': rule.rule
        }
        output.append(line)
    output.sort(key=lambda x: x['url'])
    return render_template('debug/routes/all.html',
                           title='ms365_accountcreator API – Routes',
                           routes=output)
