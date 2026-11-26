"""Builds the whole starting data set. The same insurer date gives the same data."""

from __future__ import annotations

import copy
from datetime import date

from .seed_claims import CHECKLISTS, HANDLING_GUIDE, LETTER_TEMPLATES, build_claims, build_loss_reports
from .seed_health import build_health
from .seed_investigations import build_investigations
from .seed_policy import WORDINGS, build_policies
from .seed_underwriting import build_underwriting


def build_all(today: date) -> dict:
    return {
        "wordings": copy.deepcopy(WORDINGS),
        "policies": build_policies(today),
        "claims": build_claims(today),
        "loss_reports": build_loss_reports(today),
        "claim_checklists": copy.deepcopy(CHECKLISTS),
        "handling_guide": copy.deepcopy(HANDLING_GUIDE),
        "letter_templates": copy.deepcopy(LETTER_TEMPLATES),
        **build_health(today),
        **build_underwriting(today),
        **build_investigations(today),
    }
