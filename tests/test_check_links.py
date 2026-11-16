"""Yksikkötestit verkkolinkkien tarkistimen peruslogiikalle."""
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from scripts.check_links import LinkParser, luokittele_vastaus, tee_pyyntö


class LinkCheckerTests(unittest.TestCase):
    """Testaa URL-poimintaa ja HTTP-tilojen erottelua ilman verkkoyhteyttä."""
    def test_poimii_a_elementin_href_osoitteen(self):
        parser = LinkParser()
        parser.feed('<a href="https://example.com/a">linkki</a><img src="https://example.com/i.png">')
        self.assertEqual(parser.urls, ["https://example.com/a"])

    def test_tunnistaa_uudelleenohjauksen(self):
        self.assertEqual(luokittele_vastaus(200, "https://a.example", "https://b.example"), "redirected")

    def test_tunnistaa_404_ja_410(self):
        self.assertEqual(luokittele_vastaus(404, "https://a.example", "https://a.example"), "broken")
        self.assertEqual(luokittele_vastaus(410, "https://a.example", "https://a.example"), "broken")

    def test_erottaa_estot_ja_nopeusrajat(self):
        self.assertEqual(luokittele_vastaus(403, "https://a.example", "https://a.example"), "blocked")
        self.assertEqual(luokittele_vastaus(429, "https://a.example", "https://a.example"), "rate_limited")

    def test_http_virhe_palautetaan_tilakoodina(self):
        virhe = HTTPError("https://example.com", 404, "Not Found", None, None)
        with patch("scripts.check_links.urllib.request.urlopen", side_effect=virhe):
            self.assertEqual(tee_pyyntö("https://example.com", "HEAD", 2),
                             (404, "https://example.com"))

    def test_palvelinvirhe_on_erillinen(self):
        self.assertEqual(luokittele_vastaus(503, "https://a.example", "https://a.example"), "server_error")


if __name__ == "__main__":
    unittest.main()
