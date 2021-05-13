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

        content: element.Tag = page.find("div", {"id": "content"})
        for div in content.find_all(class_="noprint"):
            div.decompose()
        for div in content.find_all(class_="printfooter"):
            div.decompose()
        for div in content.find_all("div", {"class": "mobile-hide"}):
            div.decompose()
        for ref in content.find_all("sup", {"class": "reference"}):
            ref.decompose()
        return content.get_text()
