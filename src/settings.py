# -*- coding: utf-8 -*-
import os


class Settings:
    @property
    def as_url(self) -> str:
        return os.getenv("ASSETSTORM_URL", "http://127.0.0.1:8081")

    @property
    def md_conv_url(self) -> str:
        return os.getenv("MARKDOWN2ASSETSTORM_URL", "http://127.0.0.1:8082")

    @property
    def templater_url(self) -> str:
        return os.getenv("ASSETSTORM2TEMPLATE_URL", "http://127.0.0.1:8083")
