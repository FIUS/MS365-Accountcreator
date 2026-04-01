#!/bin/bash
set -e
echo "Ensuring database tables exist..."
flask db upgrade 2>/dev/null || flask create_db
echo "Done."
