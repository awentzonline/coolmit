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

    def prepare_message(self, message):
        user_name = self.sp_check_output(
            "git config user.name", shell=True
        ).strip()
        user_email = self.sp_check_output(
            "git config user.email", shell=True
        ).strip()
        if not (user_email or user_name):
            raise Exception("You need to git config user.name and email")
        tree = self.sp_check_output(["git", "write-tree"]).strip()
        try:
            refs = self.sp_check_output("git show-ref".split()).strip()
            if refs:
                parent = self.sp_check_output(["git", "rev-parse", "HEAD"]).strip()
            else:
                parent = ""
        except subprocess.CalledProcessError:
            parent = ""
        timestamp = int(time.time())
        if parent:
            header = """tree {tree}
parent {parent}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600
gitfor """.format(
                tree=tree, parent=parent, timestamp=timestamp,
                name=user_name, email=user_email
            )
        else: # no parent commit
            header = """tree {tree}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600
gitfor """.format(
                tree=tree, timestamp=timestamp,
                name=user_name, email=user_email
            )
        body = "\n\n{}".format(message) # newline after headers and blank line
        return header, body

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

    def mine(self, prefix, message, max_probe_length=10, num_workers=4, chunk_size=100000):
        """Find a git commit which has a hash containing a desired prefix."""
        result = None
        self.pre_mine()
        for probe_length in range(1, max_probe_length + 1):
            coolmit_header, coolmit_body = self.prepare_message(message)
            git_header, coolmit_header = self.prepare_git_object(coolmit_header, coolmit_body, probe_length)
            result = self._probe(
                prefix, git_header, coolmit_body, probe_length, chunk_size)
            if result:
                salt, hash_ = result
                return coolmit_header, coolmit_body, salt, hash_

    def _probe(self, prefix, header, body, probe_length, chunk_size):
        raise NotImplemented("Implement `_probe`")
