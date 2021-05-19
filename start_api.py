import os

from backend.api import app
from backend.data_provider import base_path
from backend.utils import is_prod

if __name__ == "__main__":

    if is_prod():
        import logging

        logging.basicConfig(filename="out.log", level=logging.DEBUG)
        app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)  # , ssl_context=ssl_context)
    else:
        app.run(debug=True)
