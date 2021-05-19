import urllib.request


class PagesDownloader:
    def get_page(self, url: str):
        try:
            return urllib.request.urlopen(url)
        except Exception as ex:
            print(url, ex)
            raise ex
