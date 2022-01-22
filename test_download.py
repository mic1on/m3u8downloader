# -*- coding: utf-8 -*-
import time

from main import M3u8


def test_download():
    """测试下载"""
    m3u8_uri = 'index.m3u8'
    m3u8_key = 'ts.key'
    m3u8_d = M3u8(m3u8_uri=m3u8_uri, m3u8_key=m3u8_key, out_file_path="tmp")
    m3u8_d.download()


def test_merge():
    """测试合并"""
    m3u8_d = M3u8()
    m3u8_d.merge(ts_file_path="tmp", out_file_name=f'movie_{int(time.time())}.mp4')


if __name__ == '__main__':
    test_download()
    test_merge()
