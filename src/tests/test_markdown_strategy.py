# -*- coding: utf-8 -*-
from hypothesis import settings, given, note, Verbosity
from hypothesis.strategies import text, from_regex, one_of, lists
import unittest


word_regex = r"[a-zA-Z0-9öäüÖÄÜßáàéè€&\?\-=§\.+\/]+"
sentence_regex = r"( " + word_regex + ")*"
sentence_strategy = from_regex(r"^" + word_regex + sentence_regex + r"$", fullmatch=True)
programming_languages = r"(python|javascript|c\+\+|c#|c|bash|java|kotlin|go|docker|haskell|" + \
                        r"fortran|d|pascal|swift|rust|php|perl|r|julia|plaintext)"
mds_spans = {
    "standard": sentence_strategy,
    "em": sentence_strategy.map(lambda x: "*" + x + "*"),
    "strong": sentence_strategy.map(lambda x: "**" + x + "**"),
    "strong_em": sentence_strategy.map(lambda x: "***" + x + "***"),
    "strike_through": sentence_strategy.map(lambda x: "~~" + x + "~~"),
    "a": from_regex(r"^\[" + word_regex + sentence_regex + r"\]" +
                    r"\(https?://[\w+\.]+\)$", fullmatch=True),
    "code": sentence_strategy.map(lambda x: "`" + x + "`"),
    "fspath": from_regex(r"<fs-path>" + word_regex + sentence_regex + r"</fs-path>", fullmatch=True)
}
markdown_spans = lists(one_of(*tuple([mds_spans[key] for key in mds_spans.keys()])), min_size=1, max_size=15
                       ).map(lambda x: " ".join(x))
mds_blocks = {
    "h1": from_regex(r"^# " + word_regex + sentence_regex + r"$", fullmatch=True),
    "h2": from_regex(r"^## " + word_regex + sentence_regex + r"$", fullmatch=True),
    "h3": from_regex(r"^### " + word_regex + sentence_regex + r"$", fullmatch=True),
    "h4": from_regex(r"^#### " + word_regex + sentence_regex + r"$", fullmatch=True),
    "h5": from_regex(r"^##### " + word_regex + sentence_regex + r"$", fullmatch=True),
    "h6": from_regex(r"^###### " + word_regex + sentence_regex + r"$", fullmatch=True),
    "ol": lists(markdown_spans.map(lambda x: "1. " + x), min_size=1, max_size=15).map(lambda x: "\n".join(x)),
    "ul": lists(markdown_spans.map(lambda x: "* " + x), min_size=1, max_size=15).map(lambda x: "\n".join(x)),
    "pre": from_regex(r"^```" + programming_languages + r"\n" +
                      r"\w+([\w \(\)\[\]\{\}\:\-><\"\'\/\+\n=,#$%&|~\*;?§@]+)*\n```$", fullmatch=True),
    "img": from_regex(r"^\!\[([a-zA-Z0-9öäüÖÄÜß\-_=§\"'\.~*+\/]+( [a-zA-Z0-9öäüÖÄÜß\-_=§\"'\.~*+\/]+)*)?\]" +
                      r"\([\w+\.]+( \"" + word_regex + sentence_regex + r"\")\)$", fullmatch=True),
}
markdown_text = lists(one_of(*tuple([mds_blocks[key] for key in mds_blocks.keys()])), min_size=1, max_size=20
                      ).map(lambda x: "\n\n".join(x))


class MarkdownStrategyTestCase(unittest.TestCase):
    @settings(verbosity=Verbosity.verbose)
    @given(sentence_strategy)
    def test_words_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertEqual(1, len(t.splitlines()))

    @given(mds_spans["em"])
    def test_em_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("*"))
        self.assertTrue(t.endswith("*"))

    @given(mds_spans["strong"])
    def test_strong_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("**"))
        self.assertTrue(t.endswith("**"))

    @given(mds_spans["strong_em"])
    def test_em_strong_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("***"))
        self.assertTrue(t.endswith("***"))

    @given(mds_spans["strike_through"])
    def test_strike_through_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("~~"))
        self.assertTrue(t.endswith("~~"))

    @given(mds_spans["a"])
    def test_a_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("["))
        self.assertEqual(2, len(t.split("](")))
        self.assertTrue(t.endswith(")"), msg=t)

    @given(mds_spans["code"])
    def test_code_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("`"))
        self.assertTrue(t.endswith("`"))

    @given(mds_spans["fspath"])
    def test_fspath_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("<fs-path>"))
        self.assertTrue(t.endswith("</fs-path>"))

    @given(markdown_spans)
    def test_markdown_spans_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertEqual(1, len(t.splitlines()))

    @given(mds_blocks["pre"])
    def test_pre_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        lines = t.splitlines()
        self.assertTrue(lines[0].startswith("```"))
        self.assertTrue(lines[-1].endswith("```"))

    @given(mds_blocks["img"])
    def test_img_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        self.assertTrue(t.startswith("!["))
        self.assertEqual(2, len(t.split("](")))
        self.assertTrue(t.endswith("\")"))

    @settings(max_examples=20)
    @given(markdown_text)
    def test_markdown_text_strategy(self, t: str):
        self.assertEqual(t.strip(), t)
        environment = None
        for i, line in enumerate(t.splitlines()):
            if environment == "ol":
                if line.startswith('1. '):
                    environment = "ol"
                else:
                    environment = None
                    self.assertEqual("", line.strip())
                continue
            if environment == "ul":
                if line.startswith('* '):
                    environment = "ul"
                else:
                    environment = None
                    self.assertEqual("", line.strip())
                continue
            if environment == "pre":
                if line.endswith("```"):
                    environment = "pre-end"
                continue
            if environment not in ["pre"] and line.startswith('1. '):
                environment = "ol"
                self.assertEqual(line.strip(), line)
                continue
            if environment not in ["pre"] and line.startswith('* '):
                environment = "ul"
                self.assertEqual(line.strip(), line)
                continue
            if environment not in ["pre"] and line.startswith('```'):
                environment = "pre"
                self.assertEqual(line.lstrip(), line)
                continue
            if environment is None:
                self.assertGreater(len(line.strip()), 0)
                environment = "any"
                continue
            else:
                self.assertEqual("", line.strip())
                environment = None
                continue


if __name__ == '__main__':
    for _ in range(15):
        print("-_" + markdown_text.example() + "_-")
