import os

from OpenSSL import SSL

from backend.api import app

is_prod = os.environ["FLASK_ENV"] == "production"

if __name__ == "__main__":
    if is_prod:
        domain = "www.malin.dev"
        context = SSL.Context(SSL.TLSv1_2_METHOD)
        context.use_privatekey_file(f"/etc/letsencrypt/live/{domain}/privkey.pem")
        context.use_certificate_chain_file(f"/etc/letsencrypt/live/{domain}/fullchain.pem")
        context.use_certificate_file(f"/etc/letsencrypt/live/{domain}/cert.pem")
        app.run(debug=True, port=5000, threaded=True, ssl_context=context)

    else:
        app.run(debug=True)
