import unittest
from markdown_helpers import collapse_tree, clean_list


class MarkdownHelpersTest(unittest.TestCase):
    def test_clean_list(self):
        asset_list = [
            {'type': 'block-paragraph',
             'spans': [
                 {'type': 'span-strong', 'text': 'Foo:'},
                 {'type': 'span-regular', 'text': ' Bar.'}
             ]}
        ]
        self.assertEqual([
             {'type': 'span-strong', 'text': 'Foo:'},
             {'type': 'span-regular', 'text': ' Bar.'}
         ], clean_list(asset_list=asset_list, allowed_types=['span-strong', 'span-emphasized', 'span-regular']))

    def test_collapse_paragraphs(self):
        as_tree = {
            'type': 'toc-small',
            'id': 'skipme',
            'page': '8',
            'spans': [
                {'type': 'block-paragraph',
                 'spans': [
                     {'type': 'span-strong', 'text': 'Foo:'},
                     {'type': 'span-regular', 'text': ' Bar.'}
                 ]}
            ]
        }
        self.assertEqual({
            'type': 'toc-small',
            'id': 'skipme',
            'page': '8',
            'spans': [
                {'type': 'span-strong', 'text': 'Foo:'},
                {'type': 'span-regular', 'text': ' Bar.'}
            ]
        }, collapse_tree(as_tree, {
            'toc-small': {'page': 1, 'spans': [4]}
        }))


if __name__ == '__main__':
    unittest.main()
