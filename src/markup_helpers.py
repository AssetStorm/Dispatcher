# -*- coding: utf-8 -*-
import yaml


class MdBlock(yaml.YAMLObject):
    yaml_tag = "MD_BLOCK"

    def __init__(self, markdown):
        self.markdown = markdown

    def __str__(self) -> str:
        return "MD_BLOCK\n-->\n\n" + self.markdown + "\n\n<!---\n"

    def __repr__(self) -> str:
        return str(self)


def str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data), style='|')


yaml.add_representer(MdBlock, str_representer, yaml.Dumper)


def magic_yaml_block(data: dict) -> str:
    return "<!---\n" + yaml.dump(data) + "-->\n\n"


if __name__ == "__main__":
    d = {
        "type": "article-standard",
        "content": MdBlock("foo\n\nbar")
    }
    print(magic_yaml_block(d))
