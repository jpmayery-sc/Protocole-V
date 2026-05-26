from __future__ import annotations

from pathlib import Path

import pytest


pytestmark = pytest.mark.flow


def test_v10_checklist_tracks_current_status():
    root = Path(__file__).resolve().parents[2]
    checklist = (root / "results" / "result-analyse" / "TestV10.md").read_text(encoding="utf-8")

    required_fragments = [
        "V10 - Test experimental ECGP (rappel synthetique)",
        "## 5. Tests experimentaux restants",
        "### TEST V10-1 - Materiau",
        "### TEST V10-2 - Frequence",
        "### TEST V10-3 - Geometrie",
        "### Garde-fous critiques",
        "Condition minimale de validation finale:",
        "## 3 bis. Validation V10 recente",
        "## 6. Journal d'execution",
        "### Fiche V10-1 - Materiau",
        "### Fiche V10-2 - Frequence",
        "### Fiche V10-3 - Geometrie",
        "Regle de cloture:",
        "## 7. Paquet de validation ECGP",
        "### Sources d'appui par test",
        "V10-1 Materiau: zenodo-7313581",
        "V10-2 Frequence: zenodo-7631438",
        "V10-3 Geometrie: zenodo-5001776",
        "zenodo-7313581",
        "zenodo-7631438",
        "zenodo-10605186",
        "zenodo-5001776",
        "## 8. Checklist operationnelle ECGP stricte",
        "### Cadre commun",
        "### Champs obligatoires communs",
        "### V10-1 Materiau",
        "source d'appui: zenodo-7313581 / zenodo-7631438",
        "### Champs V10-1 obligatoires",
        "### V10-2 Frequence",
        "source d'appui: zenodo-7631438 / zenodo-5001776",
        "### Champs V10-2 obligatoires",
        "### V10-3 Geometrie",
        "source d'appui: zenodo-5001776 / zenodo-10605186",
        "### Champs V10-3 obligatoires",
        "### Cloture ECGP",
        "### Verdict final obligatoire",
        "- [ ] considerer la liste comme valide quand la suite V10, les tests pytest associes et le pont eventuel restent stables avec verdict explicite.",
    ]

    for fragment in required_fragments:
        assert fragment in checklist

    assert checklist.count("### TEST V10-") == 3
