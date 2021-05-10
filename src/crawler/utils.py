import hashlib


def normalize_url(url: str, lower: bool = True):
    if lower:
        url = url.lower()
    url = url.replace("https://", "").replace("http://", "").strip("/")
    if url.startswith("www."):
        url = url[4:]
    url = url.split("#")[0]
    return url.split("?")[0]


def encode_url(url: str):
    url = normalize_url(url)
    return hashlib.md5(url.encode()).hexdigest()
