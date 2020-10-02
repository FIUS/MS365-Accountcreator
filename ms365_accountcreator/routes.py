from flask import render_template
from . import APP

from . import api

if APP.config.get('DEBUG', False):
    from . import debug_routes



@APP.route('/')
def default_route():
    return render_template('index.html', title='muse4music')
