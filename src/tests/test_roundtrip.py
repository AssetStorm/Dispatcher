# -*- coding: utf-8 -*-
from dispatcher import app
from hypothesis import settings, given
from datetime import timedelta
from test_markdown_strategy import markdown_text
import unittest
import io


class RoundTripTestCase(unittest.TestCase):
    @settings(deadline=timedelta(milliseconds=500))
    @given(markdown_text)
    def test_md_as_md_round_trip(self, md_text):
        article_markdown = "<!---\ntype: article-standard\n" + \
                           "x_id: 1234567890123456789\n" + \
                           "catchphrase: Testartikel\n" + \
                           "column: Wissen\n" + \
                           "working_title: Standard-Testartikel\n" + \
                           "title: MD_BLOCK\n-->\n\n# Titel\n\n<!---\n" + \
                           "subtitle: MD_BLOCK\n-->\n\n## Untertitel\n\n<!---\n" + \
                           "teaser: MD_BLOCK\n-->\n\n**Vorlauftext**\n\n<!---\n" + \
                           "author: MD_BLOCK\n-->\n\nPina Merkert\n\n<!---\n" + \
                           "content: MD_BLOCK\n-->\n\n" + md_text + "\n\n<!--- -->"
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/markdown',
                                        data=data,
                                        content_type="multipart/form-data")
            self.assertEqual(200, response.status_code)
            self.assertEqual(article_markdown, str(response.data, encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()