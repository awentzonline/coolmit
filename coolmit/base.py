#!/usr/bin/env python

import string
import subprocess
import time


class CoolmitMiner(object):
    """Finds you a cool commit."""
    message_alignment = 0  # Message padding in number of chars

    def __init__(self, root_path, charset=None):
        self.root_path = root_path
        if charset is None:
            charset = string.ascii_letters
        self.charset = charset

    def sp_check_output(self, *args, **kwargs):
        kwargs["cwd"] = self.root_path
        return subprocess.check_output(*args, **kwargs)

    def get_HEAD_parts(self):
        existing_commit = self.sp_check_output(
            "git show --format=raw --no-patch", shell=True
        ).strip()
        in_header = True
        header_lines = []
        body_lines = []
        header, body = existing_commit.split('\n\n', 1)
        header = header.split('\n')
        if header[0].startswith('commit'):
            header = header[1:]  # remove first header `commit`
        if header[-1].startswith('gitfor'):  # remove old coolmit header
            header = header[:-1]
        header.append('gitfor ')
        header = '\n'.join(header)
        return header, '\n\n{}'.format(body.lstrip())

    def prepare_git_object(self, header, body, probe_length):
        len_full = len(header) + len(body) + probe_length
        if self.message_alignment:
            while True:
                msg = "commit {}\0{}{}".format(len_full + probe_length, header, body)
                if (len(msg) + probe_length) % self.message_alignment:
                    header += " "
                    len_full = len(header) + len(body) + probe_length
                else:
                    break
        return "commit {}\0{}".format(len_full, header), header

    def pre_mine(self):
        pass

    def mine(self, prefix, max_probe_length=10, num_workers=4, chunk_size=100000):
        """Find a git commit which has a hash containing a desired prefix."""
        result = None
        self.pre_mine()
        for probe_length in range(1, max_probe_length + 1):
            coolmit_header, coolmit_body = self.get_HEAD_parts()
            git_header, coolmit_header = self.prepare_git_object(
                coolmit_header, coolmit_body, probe_length)
            result = self._probe(
                prefix, git_header, coolmit_body, probe_length, chunk_size)
            if result:
                salt, hash_ = result
                return coolmit_header, coolmit_body, salt, hash_

    def _probe(self, prefix, header, body, probe_length, chunk_size):
        raise NotImplemented("Implement `_probe`")
