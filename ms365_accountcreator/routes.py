from . import APP

from . import api

if APP.config.get('DEBUG', False):
    from . import debug_routes
