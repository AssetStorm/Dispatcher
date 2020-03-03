# -*- coding: utf-8 -*-
from dispatcher import app
from hypothesis import settings, given
from datetime import timedelta
from markdown_helpers import collapse_tree
from test_markdown_strategy import markdown_text
from settings import Settings
import unittest
import requests
import json
import io
import os


class RoundTripTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        requests.delete(Settings().as_url + "/delete_all_assets")

    def md_as_md_article_round_trip(self, md_text):
        article_markdown = "<!---\ntype: article-standard\n" + \
                           "x_id: 1234567890123456789\n" + \
                           "catchphrase: Testartikel\n" + \
                           "column: Wissen\n" + \
                           "working_title: Standard-Testartikel\n" + \
                           "title: MD_BLOCK\n-->\n\n# Titel\n\n<!---\n" + \
                           "subtitle: MD_BLOCK\n-->\n\n## Untertitel\n\n<!---\n" + \
                           "teaser: MD_BLOCK\n-->\n\n**Vorlauftext**\n\n<!---\n" + \
                           "author: MD_BLOCK\n-->\n\nPina Merkert\n\n<!---\n" + \
                           "content: MD_BLOCK\n-->\n\n" + md_text + "\n\n<!---\n" + \
                           "article_link:\n" + \
                           "  type: article-link-container\n" + \
                           "  link_description: Dokumentation\n" + \
                           "  link: <ctlink />\n" + \
                           "bibliography:\n-->"
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/markdown',
                                        data=data,
                                        content_type="multipart/form-data")
            if response.status_code != 200:
                print(response.data)
                print("Input:")
                print(md_text)
                print("---------------")
                print(response.data)
                print("===============")
            self.assertEqual(200, response.status_code)
            self.assertEqual(article_markdown, str(response.data, encoding='utf-8'))

    def as_through_md_round_trip(self, article: dict):
        with app.test_client() as test_client:
            response = test_client.post('/convert/assetstorm/markdown',
                                        data=json.dumps(article, ensure_ascii=False).encode('utf-8'),
                                        content_type="application/json")
            if response.status_code != 200:
                print(response.data)
                print("Input:")
                print(json.dumps(article, indent=2))
                print("---------------")
                print(response.data)
                print("===============")
            self.assertEqual(200, response.status_code)
            md_converter_response = requests.post(
                Settings().md_conv_url + "/",
                data=response.data)
            md_converter_response.encoding = 'utf-8'
            converted_tree = md_converter_response.json()
            as_tree = collapse_tree(converted_tree['blocks'][0])
            self.assertEqual(article, as_tree)

    @settings(deadline=timedelta(milliseconds=1000), max_examples=10)
    @given(markdown_text)
    def test_md_as_md_round_trip(self, md_text: str):
        self.md_as_md_article_round_trip(md_text)

    def test_unicode_in_md_as_md_round_trip(self):
        self.md_as_md_article_round_trip("# üöäÜÖÄß foo")

    def test_toc_round_trip(self):
        with open(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "example_toc.json"), 'r') as toc_json_file:
            toc = json.load(toc_json_file)
        self.as_through_md_round_trip(toc)


if __name__ == '__main__':
    unittest.main()
