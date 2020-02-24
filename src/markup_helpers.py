# -*- coding: utf-8 -*-
import yaml


class MdBlock(yaml.YAMLObject):
    yaml_tag = "MD_BLOCK"

    def __init__(self, markdown):
        self.markdown = markdown

    def __str__(self) -> str:
        return "MD_BLOCK\n-->\n\n" + self.markdown + "\n\n<!--- "

    def __repr__(self) -> str:
        return str(self)


def str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data), style='|')


yaml.add_representer(MdBlock, str_representer, yaml.Dumper)


def magic_yaml_block(data: dict) -> str:
    md = "<!---"
    for key in data:
        if type(data[key]) in [int, float, str]:
            md += "\n" + str(key) + ": " + data[key]
        elif type(data[key]) is dict:
            md += "\n" + str(key) + ": \n" + "\n".join(["  " + line for line in yaml.safe_dump(data[key]).splitlines()])
        else:
            md += "\n" + str(key) + ": " + str(data[key])
    md += "\n-->\n\n"
    return md


if __name__ == "__main__":
    d = {
        "type": "article-standard",
        "content": MdBlock("foo\n\nbar")
    }
    print(magic_yaml_block(d))
