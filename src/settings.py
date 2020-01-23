# -*- coding: utf-8 -*-
import os


class Settings:
    @property
    def md_conv_url(self) -> str:
        return os.getenv("MARKDOWN2ASSETSTORM_URL", "http://127.0.0.1:8082")
