# -*- coding: utf-8 -*-
import glob
import os
from concurrent.futures import ThreadPoolExecutor

import m3u8
from m3u8.parser import urljoin

from downloader import Downloader


class M3u8(object):

    def __init__(self, m3u8_uri=None, m3u8_key=None, out_file_path=None):
        """
        :param m3u8_uri: m3u8网址或本地文件
        :param m3u8_key: m3u8加密key
            如果m3u8为加密视频，则需要提供key
                - 当m3u8_uri为网址时会自动下载key
                - 当m3u8_uri为本地文件时需提供key文件路径
        :param out_file_path: 输出下载后ts的文件夹
        """
        self.m3u8_uri = m3u8_uri
        self.m3u8_key = m3u8_key
        self.out_file_path = out_file_path or '.'

    def download(self, workers=20):
        """
        下载ts文件
        :param workers: 最大工作线程数
        """
        if not self.m3u8_uri:
            raise ValueError('miss m3u8 uri')
        play_list = m3u8.load(self.m3u8_uri)
        if self.m3u8_key:
            key_uri = self.m3u8_key
        else:
            key = play_list.keys[0]
            key_uri = None if key is None else urljoin(key.base_uri, key.uri)
        file_urls = [urljoin(play_list.base_uri, file) for file in play_list.segments.uri]
        d = Downloader(self.out_file_path, key_uri=key_uri)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pool.map(d.download, file_urls)
        return d.files

    def merge(self, ts_file_path=None, out_file_name=None, delete_on_finish=True):
        """
        合并ts文件
        :param ts_file_path: 被合并的ts文件夹，自动提取文件夹中所有.ts文件
        :param out_file_name: 要输出的文件名，默认video.mp4
        :param delete_on_finish: 合并完成后删除ts
        """
        ts_file_path = ts_file_path or self.out_file_path
        out_file_name = out_file_name or 'video.mp4'
        out_file = os.path.join(ts_file_path, out_file_name)

        _ts_file_path = glob.glob(os.path.join(ts_file_path, '*.ts'))
        ts_files = [os.path.split(ts)[1] for ts in _ts_file_path]
        ts_files.sort(key=lambda x: x[0:len(x) - 3])
        if not ts_files:
            return
        with open(out_file, mode='wb+') as f:
            for _, ts in enumerate(ts_files):
                ts_path = os.path.join(ts_file_path, ts)
                f.write(open(ts_path, mode='rb').read())

        if delete_on_finish:
            [os.remove(ts_file) for ts_file in _ts_file_path]