import os

from backend.api import app
from backend.data_provider import base_path
from backend.utils import is_prod

print("Environment", os.environ["FLASK_ENV"], base_path())
if __name__ == "__main__":

    if is_prod():
        domain = "www.malin.dev"
        ssl_context = (f"/etc/letsencrypt/live/{domain}/fullchain.pem", f"/etc/letsencrypt/live/{domain}/privkey.pem")
        app.run(debug=True, port=5000, threaded=True, ssl_context=ssl_context)
    else:
        app.run(debug=True)
