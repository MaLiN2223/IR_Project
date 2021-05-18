import os

from OpenSSL import SSL

from backend.api import app

is_prod = os.environ["FLASK_ENV"] == "production"

if __name__ == "__main__":
    print(
        "Environment",
    )
    if is_prod:
        domain = "www.malin.dev"
        ssl_context = (f"/etc/letsencrypt/live/{domain}/fullchain.pem", f"/etc/letsencrypt/live/{domain}/privkey.pem")
        app.run(debug=True, port=5000, threaded=True, ssl_context=ssl_context)

    else:
        app.run(debug=True)
