"""Entry point for running the development server."""

import os

os.environ.setdefault('PGCLIENTENCODING', 'utf8')

from app.factory import create_app  # noqa: E402

application = create_app()

if __name__ == '__main__':
    import logging

    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    port = int(os.environ.get('PORT', 5000))
    print(' * Aviasales API: http://127.0.0.1:{0}'.format(port))
    print(' * GET /api/flights')
    print(' * GET /api/flights/extremes')
    print(' * GET /api/diff')
    application.run(host='0.0.0.0', port=port, debug=False)
