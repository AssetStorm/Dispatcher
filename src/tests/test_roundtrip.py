# -*- coding: utf-8 -*-
from dispatcher import app
from hypothesis import settings, given
from datetime import timedelta
from test_markdown_strategy import markdown_text
import unittest
import io


class RoundTripTestCase(unittest.TestCase):
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

    @settings(deadline=timedelta(milliseconds=1000), max_examples=10)
    @given(markdown_text)
    def test_md_as_md_round_trip(self, md_text: str):
        self.md_as_md_article_round_trip(md_text)

    def test_unicode_in_md_as_md_round_trip(self):
        self.md_as_md_article_round_trip("# üöäÜÖÄß foo")


if __name__ == '__main__':
    unittest.main()
