# -*- coding: utf-8 -*-
import hashlib


def hash_file(fp) -> str:
    buffer_size = 65536
    sha1 = hashlib.sha1()
    while True:
        data_chunk = fp.read(buffer_size)
        if not data_chunk:
            break
        sha1.update(data_chunk)
    return sha1.hexdigest()
