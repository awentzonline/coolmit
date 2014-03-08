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
            body = """tree {tree}
parent {parent}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600

{message} """.format(
                tree=tree, parent=parent, timestamp=timestamp, message=message,
                name=user_name, email=user_email
            )
        else: # no parent commit
            body = """tree {tree}
author {name} <{email}> {timestamp} -0600
committer {name} <{email}> {timestamp} -0600

{message} """.format(
                tree=tree, timestamp=timestamp, message=message,
                name=user_name, email=user_email
            )
        return body

    def prepare_git_object(self, body, probe_length):
        if self.message_alignment:
            protocol_len = len("commit \0")
            while True:
                total_len = (
                    protocol_len +
                    len(str(len(body) + probe_length)) +
                    len(body) +
                    probe_length
                )
                if total_len % self.message_alignment:
                    body += " "
                else:
                    break
        return "commit {}\0{}".format(len(body) + probe_length, body)

    def pre_mine(self):
        pass

    def mine(self, prefix, message, max_probe_length=10, num_workers=4, chunk_size=100000):
        """Find a git commit which has a hash containing a desired prefix."""
        result = None
        self.pre_mine()
        for probe_length in range(1, max_probe_length + 1):
            coolmit_msg = self.prepare_message(message)
            template = self.prepare_git_object(coolmit_msg, probe_length)
            result = self._probe(prefix, template, probe_length, chunk_size)
            if result:
                salt, hash_ = result
                return coolmit_msg, salt, hash_

    def _probe(self, prefix, message, probe_length, chunk_size):
        raise NotImplemented("Implement `_probe`")
