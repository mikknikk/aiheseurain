"""Testaa seurantakohteiden ja julkaisureititysten viitteiden eheys."""
import json, shutil, tempfile, unittest
from pathlib import Path
from scripts.validate_target_publication import validate, ROOT
class TargetPublicationTests(unittest.TestCase):
    def test_production_registries_are_consistent(self): self.assertEqual(validate(), [])
    def test_route_rejects_multiple_publications(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ["schemas","data","modules"]: shutil.copytree(ROOT/name,root/name)
            path=root/"data/publication-routing.json"; route=json.loads(path.read_text(encoding="utf-8"))
            route["routes"]=[{"route_id":"bad","module_ref":"indian-film-screening-watch","target_ref":"indian-film-screening-watch.all-indian-film-screenings-finland","publication_refs":["one","two"],"observation_types":["film-screening"],"status":"inactive"}]
            path.write_text(json.dumps(route),encoding="utf-8")
            self.assertTrue(any("täsmälleen yksi julkaisukohde" in error for error in validate(root)))
    def test_unknown_publication_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ["schemas","data","modules"]: shutil.copytree(ROOT/name,root/name)
            path=root/"data/publication-routing.json"; route=json.loads(path.read_text(encoding="utf-8"))
            route["routes"]=[{"route_id":"bad","module_ref":"indian-film-screening-watch","target_ref":"indian-film-screening-watch.all-indian-film-screenings-finland","publication_refs":["missing-feed"],"observation_types":["film-screening"],"status":"inactive"}]
            path.write_text(json.dumps(route),encoding="utf-8")
            self.assertTrue(any("Tuntematon julkaisukohde" in error for error in validate(root)))
if __name__=="__main__": unittest.main()
