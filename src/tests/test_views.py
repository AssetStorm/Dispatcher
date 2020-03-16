# -*- coding: utf-8 -*-
from dispatcher import app
from flask import Response
from markup_helpers import MdBlock, magic_yaml_block
from unittest.mock import patch
import unittest
import io
import os


class TestConvertMarkdown(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True

    def request_with_error(self, data: dict) -> Response:
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/proof_html',
                                        data=data,
                                        content_type="multipart/form-data")
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        return response

    def test_uplaod_no_text(self):
        data = {'image.jpg': (io.BytesIO(b"123"), "image.jpg")}
        response = self.request_with_error(data)
        self.assertEqual({"Error": "There was no .md or .txt file in the upload."},
                         response.get_json())

    def test_upload_no_unicode(self):
        data = {'no_unicode.md': (io.BytesIO(b"abc\xc3\x00123"), "no_unicode.md")}
        response = self.request_with_error(data)
        self.assertEqual({"Error": "The uploaded markdown was not encoded as UTF-8."},
                         response.get_json())

    def test_upload_empty_document(self):
        data = {'article.md': (io.BytesIO("".encode('utf-8')), "article.md")}
        response = self.request_with_error(data)
        self.assertEqual({"Error": "The document was empty."},
                         response.get_json())

    def test_upload_file_without_header(self):
        data = {
            'article.md': (io.BytesIO("# Markdown\n\nWith text.".encode('utf-8')), "article.md"),
            'image.jpg': (io.BytesIO(b"123"), "image.jpg")
        }
        response = self.request_with_error(data)
        self.assertEqual({"Error": "The document must contain exactly one article. Did you forget the header?"},
                         response.get_json())

    def test_upload_typeless_header(self):
        article_markdown = "<!---\n"
        article_markdown += "foo: bar\n"
        article_markdown += "-->"
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        response = self.request_with_error(data)
        self.assertEqual({"Error": "The document was empty."},
                         response.get_json())

    def test_upload_missing_x_id(self):
        article_markdown = magic_yaml_block({
            "type": "article-standard",
            "catchphrase": "Testartikel",
            "column": "Wissen",
            "working_title": "Standard-Testartikel",
            "title": MdBlock("# Titel"),
            "subtitle": MdBlock("## Untertitel"),
            "teaser": MdBlock("**Vorlauftext**"),
            "author": MdBlock("Pina Merkert"),
            "content": MdBlock("Text des Artikels.\n\nMehrere Absätze")
        })
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        response = self.request_with_error(data)
        self.assertEqual({"Error": "The article-standard misses a x_id. Please add a \"x_id\" key."},
                         response.get_json())

    def test_convert(self):
        article_markdown = magic_yaml_block({
            "type": "article-standard",
            "x_id": "1234567890123456789",
            "catchphrase": "Testartikel",
            "column": "Wissen",
            "working_title": "Standard-Testartikel",
            "title": MdBlock("# Titel"),
            "subtitle": MdBlock("## Untertitel"),
            "teaser": MdBlock("**Vorlauftext**"),
            "author": MdBlock("Pina Merkert"),
            "content": MdBlock("Text des Artikels.\n\nMehrere Absätze"),
            "article_link": {"type": "article-link-container",
                             "link_description": "Dokumentation",
                             "link": {"type": "span-ct-link"}},
            "bibliography": []
        })
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/proof_html',
                                        data=data,
                                        content_type="multipart/form-data")
            self.assertEqual(200, response.status_code)
            self.assertEqual(
                "<article-standard>" +
                "<x_id>1234567890123456789</x_id>" +
                "<catchphrase>Testartikel</catchphrase>" +
                "<magazine-column>Wissen</magazine-column>" +
                "<h1>Titel</h1>" +
                "<h2 class=\"subtitle\">Untertitel</h2>" +
                "<teaser>Vorlauftext</teaser>" +
                "<author>Von Pina Merkert</author>" +
                "<p>Text des Artikels.</p><p>Mehrere Absätze</p>" +
                "<article-link>" +
                "<article-link-description>Dokumentation:</article-link-description> <ctlink />" +
                "</article-link>" +
                "<div class=\"bibliography\"><h3>Literatur</h3><ol></ol></div>" +
                "</article-standard>", str(response.data, encoding='utf-8'))

    def test_standard_article_with_email_link(self):
        article_markdown = magic_yaml_block({
            "type": "article-standard",
            "x_id": "1234567890123456789",
            "catchphrase": "Testartikel",
            "column": "Wissen",
            "working_title": "Standard-Testartikel",
            "title": MdBlock("# Titel"),
            "subtitle": MdBlock("## Untertitel"),
            "teaser": MdBlock("**Vorlauftext**"),
            "author": MdBlock("Pina Merkert"),
            "content": MdBlock("Text des Artikels.\n\nAbsatz mit Mailto: [pmk@ct.de](mailto:pmk@ct.de)\n\nAbsatz 3."),
            "article_link": {"type": "article-link-container",
                             "link_description": "Dokumentation",
                             "link": {"type": "span-ct-link"}},
            "bibliography": []
        })
        data = {'article.md': (io.BytesIO(article_markdown.encode('utf-8')), "article.md")}
        with app.test_client() as test_client:
            response = test_client.post('/convert/markdown/proof_html',
                                        data=data,
                                        content_type="multipart/form-data")
            self.assertEqual(200, response.status_code)
            self.assertEqual(
                "<article-standard>" +
                "<x_id>1234567890123456789</x_id>" +
                "<catchphrase>Testartikel</catchphrase>" +
                "<magazine-column>Wissen</magazine-column>" +
                "<h1>Titel</h1>" +
                "<h2 class=\"subtitle\">Untertitel</h2>" +
                "<teaser>Vorlauftext</teaser>" +
                "<author>Von Pina Merkert</author>" +
                "<p>Text des Artikels.</p><p>Absatz mit Mailto: " +
                "<a href=\"mailto:pmk@ct.de\">pmk@ct.de</a></p>" +
                "<p>Absatz 3.</p>" +
                "<article-link>" +
                "<article-link-description>Dokumentation:</article-link-description> <ctlink />" +
                "</article-link>" +
                "<div class=\"bibliography\"><h3>Literatur</h3><ol></ol></div>" +
                "</article-standard>", str(response.data, encoding='utf-8'))

    def test_example_article_markdown(self):
        filename = 'example-article.md'
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
        with open(file_path, 'rb') as ea_fp:
            data = {filename: ea_fp}
            with app.test_client() as test_client:
                response = test_client.post('/convert/markdown/markdown',
                                            data=data,
                                            content_type="multipart/form-data")
                self.assertEqual(200, response.status_code)
                loaded_markdown = str(response.data, encoding='utf-8')
        with open(file_path, 'rb') as ea_fp:
            self.assertEqual(str(ea_fp.read(), encoding='utf-8'), loaded_markdown)

    def test_example_article_sy_xml(self):
        filename = 'example-article.md'
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
        with open(file_path, 'rb') as ea_fp:
            data = {filename: ea_fp}
            with app.test_client() as test_client:
                response = test_client.post('/convert/markdown/sy_xml',
                                            data=data,
                                            content_type="multipart/form-data")
                self.assertEqual(200, response.status_code)
                loaded_xml = str(response.data, encoding='utf-8')
        print(loaded_xml)
        self.assertEqual(
            "<document dbref=\"1234567890123456789\">\n" +
            "<title>Untertitel</title>\n<subtitle>Titel</subtitle>\n<abstract>Vorlauftext</abstract>\n" +
            "<textel>\n" +
            "<paragraph type=\"standard\" id=\"e0\">Text des Artikels.</paragraph>\n" +
            "<paragraph type=\"standard\" id=\"e1\">Dies ist ein zweiter Absatz.</paragraph>\n" +
            "<shorturlwrapper><label>Dokumentation: </label><shorturl></shorturl></shorturlwrapper>\n" +
            "<bibliography><title>Literatur</title>" +
            "<internal brand=\"ct\" year=\"19\" month=\"17\" page=\"127\">" +
            "Pina Merkert, Djangolino, Webentwicklung mit Django und wenig Code, c't 17/19, S. 127</internal>" +
            "<external href=\"https://ct.de\">https://ct.de</external></bibliography>\n" +
            "</textel>\n</document>", loaded_xml)

    def two_file_conversion(self, source_path, target_example_path, source_format, target_format):
        with open(source_path, 'rb') as source_file:
            data = {os.path.split(source_path)[-1]: source_file}
            with app.test_client() as test_client:
                response = test_client.post("/convert/{}/{}".format(source_format, target_format),
                                            data=data,
                                            content_type="multipart/form-data")
                self.assertEqual(200, response.status_code)
                converted = str(response.data, encoding='utf-8')
        print(converted)
        with open(target_example_path, 'rb') as target_example_file:
            self.assertEqual(converted, target_example_file.read())

    def test_articles_folder(self):
        extensions = {
            "sy_xml": "xml",
            "markdown": "md",
            "assetstorm": "json"
        }
        base_path = os.path.dirname(os.path.realpath(__file__))
        example_folders = os.listdir(os.path.join(base_path, "articles"))
        for source_folder in ["markdown", "assetstorm"]:
            if not os.path.isdir(os.path.join(base_path, "articles", source_folder)):
                continue
            for target_folder in example_folders:
                if not os.path.isdir(os.path.join(base_path, "articles", target_folder)):
                    continue
                for source_filename in os.listdir(os.path.join(base_path, "articles", source_folder)):
                    source_file_path = os.path.join(
                        base_path, "articles", source_folder, source_filename)
                    if not os.path.isfile(source_file_path):
                        continue
                    target_file_path = os.path.join(
                        base_path, "articles", target_folder,
                        source_filename.split('.')[0] + '.' +
                        extensions[target_folder] if target_folder in extensions.keys() else 'txt')
                    if os.path.isfile(target_file_path):
                        self.two_file_conversion(source_file_path, target_file_path)


class TestDeliverOpenApiDefinition(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True

    def test_default_first_server(self):
        with app.test_client() as test_client:
            response = test_client.get('/openapi.json')
            self.assertEqual(200, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            api_def = response.get_json()
        self.assertEqual('3.0.0', api_def['openapi'])
        self.assertEqual('AssetStorm-Dispatcher', api_def['info']['title'])
        self.assertEqual({'url': 'http://dispatcher.assetstorm.pinae.net'}, api_def['servers'][0])

    @patch('os.getenv', lambda *key: {
        'SERVER_NAME': 'https://test.org/foo/bar/baz'
    }[key[0]])
    def test_server_by_env(self):
        with app.test_client() as test_client:
            response = test_client.get('/openapi.json')
            self.assertEqual(200, response.status_code)
            self.assertEqual("application/json", response.mimetype)
            api_def = response.get_json()
        self.assertEqual({'url': 'https://test.org/foo/bar/baz'}, api_def['servers'][0])


class TestLive(unittest.TestCase):
    def setUp(self) -> None:
        app.testing = True

    def test_standard_live(self):
        with app.test_client() as test_client:
            response = test_client.get('/live')
            self.assertEqual(200, response.status_code)

    @patch('os.getenv', lambda *key: {
        'MARKDOWN2ASSETSTORM_URL': 'https://wrong.url/not/existing'
    }[key[0]])
    def test_converter_unreachable(self):
        with app.test_client() as test_client:
            response = test_client.get('/live')
            self.assertEqual(400, response.status_code)
            self.assertEqual({'Error': 'The url https://wrong.url/not/existing/live is unreachable.'},
                             response.get_json())


if __name__ == '__main__':  # pragma: no mutate
    unittest.main()  # pragma: no cover
