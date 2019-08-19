# -*- coding: utf-8 -*-
import re
from unittest import TestCase
from flask_beet.utils import unique_request_id


class Testcases(TestCase):
    def test_new_username(self):
        x = unique_request_id()
        assert re.match(
            r"^[a-f0-9-]{8}-[a-f0-9-]{4}-[a-f0-9-]{4}-[a-f0-9-]{4}-[a-f0-9-]{12}$", x
        )
