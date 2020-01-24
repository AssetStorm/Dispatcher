# -*- coding: utf-8 -*-
from dispatcher import app
from test.support import EnvironmentVarGuard
import unittest


class TestConvertMarkdown(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True

    def test_convert_no_content(self):
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/proof_html')
            self.assertEqual(400, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            self.assertEqual({"Error": "An error occurred while converting the markdown document."},
                             response.get_json())

    def test_convert(self):
        with app.test_client() as test_client:
            response = test_client.post(
                '/convert/markdown/proof_html', data="<!---\n" +
                "type: article-standard\n" +
                "x_id: \"\"\n" +
                "title: MD_BLOCK\n-->\n# Titel\n\n<!---\n" +
                "subtitle: MD_BLOCK\n-->\n## Untertitel\n\n<!---\n" +
                "teaser: MD_BLOCK\n-->\n**Vorlauftext**\n\n<!---\n" +
                "author: MD_BLOCK\n-->\nPina Merkert\n\n<!---\n" +
                "content: MD_BLOCK\n-->\n" +
                "Text des Artikels.\n\n" +
                "Mehrere Absätze\n\n" +
                "<!--- -->")
            #self.assertEqual(200, response.status_code)
            self.assertEqual("<div>foo</div>", str(response.data, encoding='utf-8'))


class TestDeliverOpenApiDefinition(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True
        self.env = EnvironmentVarGuard()

    def test_default_first_server(self):
        with app.test_client() as test_client:
            response = test_client.get('/openapi.json')
            self.assertEqual(200, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            api_def = response.get_json()
        self.assertEqual('3.0.0', api_def['openapi'])
        self.assertEqual('AssetStorm-Dispatcher', api_def['info']['title'])
        self.assertEqual({'url': 'http://dispatcher.assetstorm.pinae.net'}, api_def['servers'][0])

    def test_server_by_env(self):
        self.env.set('SERVER_NAME', 'https://test.org/foo/bar/baz')
        with self.env:
            with app.test_client() as test_client:
                response = test_client.get('/openapi.json')
                self.assertEqual(200, response.status_code)
                self.assertEqual("application/json", response.mimetype)
                api_def = response.get_json()
            self.assertEqual({'url': 'https://test.org/foo/bar/baz'}, api_def['servers'][0])


class TestLive(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True
        self.env = EnvironmentVarGuard()

    def test_standard_live(self):
        with app.test_client() as test_client:
            response = test_client.get('/live')
            self.assertEqual(200, response.status_code)

    def test_converter_unreachable(self):
        self.env.set('MARKDOWN2ASSETSTORM_URL', 'https://wrong.url/not/existing')
        with self.env:
            with app.test_client() as test_client:
                response = test_client.get('/live')
                self.assertEqual(400, response.status_code)
                self.assertEqual({'Error': 'The url https://wrong.url/not/existing/live is unreachable.'},
                                 response.get_json())


if __name__ == '__main__':  # pragma: no mutate
    unittest.main()  # pragma: no cover
