import os
import unittest

from pyrentri import RentriWrapper
from pyrentri.rentri_enum import RENTRIStatus


def _has_valid_config() -> bool:
    return os.path.exists("config.ini") or os.path.exists("test/config.ini")


@unittest.skipUnless(
    _has_valid_config(),
    "Test di integrazione saltati: config.ini o certificato P12 non disponibili nell'ambiente"
)
class TestRentri(unittest.TestCase):
    """
    author: Antonio Porcelli
    username: Progressify
    github: https://github.com/progressify
    site: https://progressify.dev
    ig: https://www.instagram.com/progressify/
    """

    def setUp(self):
        config_path = "./" if os.path.exists("config.ini") else "./test/"
        self.rentri = RentriWrapper(config_path=config_path)

    def test_status_anagrafiche_api(self):
        status, payload = self.rentri.status_api("anagrafiche")
        if payload.get("status") == "Warning":
            self.assertEqual(status, RENTRIStatus.WARNING)
        else:
            self.assertEqual(status, RENTRIStatus.OK)

    def test_status_formulari_api(self):
        status, payload = self.rentri.status_api("formulari")
        if payload.get("status") == "Warning":
            self.assertEqual(status, RENTRIStatus.WARNING)
        else:
            self.assertEqual(status, RENTRIStatus.OK)
