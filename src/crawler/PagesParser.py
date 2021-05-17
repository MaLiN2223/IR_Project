from typing import List

from bs4 import BeautifulSoup, element


class PagesParser:
    def extract_links(self, soup: BeautifulSoup) -> List[str]:
        links = []
        for link in soup.findAll("a"):
            url = link.get("href")
            if url is not None:
                links.append(url)
        return links

    def get_pure_page_text(self, page: BeautifulSoup) -> str:
        class_to_remove = ["references-small", "mw-references-wrap", "mobile-hide", "printfooter", "noprint", "pBody", "reference", "external text"]

        content: element.Tag = page.find("div", {"id": "content"})
        for ref in content.find_all("sup", {"class": "reference"}):
            ref.decompose()

        for _class in class_to_remove:
            for div in content.find_all(class_=_class):
                div.decompose()

        return content.get_text()
