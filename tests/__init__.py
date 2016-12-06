import os
import tempfile
import shutil
import subprocess
import unittest

import coolmit
from coolmit.base import CoolmitMiner


def touch(path):
    with open(path, "a"):
        os.utime(path, None)


class BaseCoolmitTestCase(unittest.TestCase):
    def setUp(self):
        self.root_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root_path)

    def sp_call(self, *args, **kwargs):
        kwargs["cwd"] = self.root_path
        return subprocess.call(*args, **kwargs)

    def sp_check_output(self, *args, **kwargs):
        kwargs["cwd"] = self.rool_path
        return subprocess.check_output(*args, **kwargs)

    def init_repo(self):
        return self.sp_call("git init", shell=True)

    def setup_test_user(self, name="Steve Ballmer", email="bigpoppa@microsoft.com"):
        self.sp_call("git config user.name \"{}\"".format(name), shell=True)
        self.sp_call("git config user.email \"{}\"".format(email), shell=True)

    def touch_file(self, name):
        return touch(os.path.join(self.root_path, name))


class CoolmitMetaTestCase(BaseCoolmitTestCase):
    """Tests the tests."""
    def test_init_repo(self):
        self.assertEqual(self.init_repo(), 0)

    def test_touch_file(self):
        filename = "foobar"
        abs_path = os.path.join(self.root_path, filename)
        self.assertFalse(os.path.exists(abs_path))
        self.touch_file(filename)
        self.assertTrue(os.path.exists(abs_path))


class CoolmitTestCase(BaseCoolmitTestCase):
    message_alignment = 0
    prefix = "beef"

    def setUp(self):
        CoolmitMiner.message_alignment = self.message_alignment
        super(CoolmitTestCase, self).setUp()

    def tearDown(self):
        super(CoolmitTestCase, self).tearDown()
        CoolmitMiner.message_alignment = self.message_alignment

    def test_coolmit(self):
        self.init_repo()
        self.setup_test_user()
        self.touch_file("AirWolf.plans")
        self.sp_call("git add .", shell=True)
        self.sp_call("git commit -m \"Testing\"", shell=True)
        result_hash = coolmit.coolmit(
            self.root_path, self.prefix,
            chunk_size=10000, num_workers=5
        )
        if not result_hash.startswith(self.prefix):
            print("*********{}*********".format(result_hash))
        self.assertTrue(result_hash.startswith(self.prefix))


class CoolmitTestAlignment(CoolmitTestCase):
    """Test padded messages"""
    message_alignment = 4
