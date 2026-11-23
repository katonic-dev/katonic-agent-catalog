"""Seed data, part 7: publications of an invented regulator, the Meridia Financial Conduct Authority (invented).

Each publication is written to give a known result when it is compared with the policies in
banking/policy-library (MTB-POL-014, MTB-POL-021, MTB-POL-033, MTB-STD-041). SCENARIOS.md lists the right verdicts.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago

REGULATOR_NAME = "Meridia Financial Conduct Authority (invented)"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def long_date(d: date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def _pub(pid: str, kind: str, ago: int, title: str, summary: str, binding: bool, paras: list[str], today: date) -> dict:
    return {"publication_id": pid, "kind": kind, "published": d_ago(today, ago), "title": title, "summary": summary,
            "binding": binding, "paragraphs": paras}


def build_publications(today: date) -> dict:
    def eff(ago: int, days: int) -> str:
        return long_date(today - timedelta(days=ago) + timedelta(days=days))

    pubs = [
        _pub("MFCA-2026-029", "circular", 57, "Circular 2026/07: Handling of coins and banknotes at branches",
             "Rules for counting, storing and exchanging coins and banknotes at bank branches.", True, [
                 "This circular sets out how a bank branch handles coins and banknotes.",
                 "A branch must count every cash delivery in the presence of two staff members and record the result.",
                 "A branch must exchange a damaged banknote for a customer if more than half of the note is present.",
                 "A branch must keep a counterfeit banknote out of circulation and hand it to the regulator's currency "
                 "desk within 24 hours.",
                 f"This circular takes effect on {eff(57, 60)}."], today),
        _pub("MFCA-2026-033", "guideline", 44, "Guideline 2026/04: Human review of generative AI output sent to customers",
             "A bank must have a person review each output of a generative AI system before it reaches a customer, "
             "record who reviewed it, and tell staff which systems use AI.", True, [
                 "This guideline applies to a bank that uses a generative artificial intelligence system to draft text "
                 "that is sent to a customer.",
                 "A bank must make sure that a person reviews every output of a generative AI system before it is sent "
                 "to a customer.",
                 "A bank must record the name of the person who reviewed each output.",
                 "A bank must tell its staff which systems use artificial intelligence and what each system may and "
                 "may not do.",
                 f"This guideline takes effect on {eff(44, 90)}."], today),
        _pub("MFCA-2026-036", "guideline", 31, "Guideline 2026/05: Assessing a supplier's own use of artificial intelligence",
             "A bank must assess how a supplier uses artificial intelligence in the service it supplies, before it "
             "approves the supplier and every year after.", True, [
                 "This guideline applies to a bank that obtains a service from a supplier whose service uses "
                 "artificial intelligence.",
                 "Before it approves such a supplier, a bank must ask the supplier to describe each artificial "
                 "intelligence system in the service, the data it uses, and whether bank or customer information was "
                 "used to train it.",
                 "A bank must assess how the supplier validates and monitors each system, and how a person reviews its "
                 "outputs.",
                 "A bank must repeat the assessment at least once a year and after any material change to the service.",
                 "A bank must record the assessment and the decision and give both to the committee that approves the "
                 "supplier.",
                 f"This guideline takes effect on {eff(31, 120)}."], today),
        _pub("MFCA-2026-040", "notice", 18, "Notice 2026/09: Reporting technology incidents that affect customers",
             "A bank must report a technology incident that affects customers to the regulator within four hours of "
             "detecting it.", True, [
                 "This notice sets the period for reporting a technology incident that affects customers.",
                 "A bank must report such an incident to the regulator within four hours of detecting it, using the "
                 "regulator's incident form.",
                 "A bank must report even if the cause is not yet known. It must send a full report within five "
                 "working days.",
                 f"This notice takes effect on {eff(18, 30)}."], today),
        _pub("MFCA-2026-043", "consultation paper", 9,
             "Consultation paper 2026/03: Telling customers when AI contributed to a decision about them",
             "The regulator asks for comments on a proposal that banks tell customers, in plain language, when "
             "artificial intelligence contributed to a decision about them. Not yet binding.", False, [
                 "This is a consultation paper. It is not binding and creates no duty for any bank.",
                 "The regulator proposes that a bank tells a customer, in plain language, when artificial intelligence "
                 "contributed to a decision about that customer.",
                 "The regulator proposes that the notice is given at the time of the decision and says how the customer "
                 "can ask for a person to look at it again.",
                 f"Comments are open until {eff(9, 30)}. The regulator will publish its decision after it has read them."],
             today),
        _pub("MFCA-2026-045", "circular", 3, "Circular 2026/08: Customer information shared with other institutions "
             "through a shared platform",
             "A bank that shares customer information with other institutions through a shared platform must have a "
             "consent mechanism, a common data format and a dispute process.", True, [
                 "This circular applies to a bank that shares customer information with other financial institutions at "
                 "the customer's request, through a shared platform.",
                 "A bank must give the customer a way to consent to each sharing arrangement, to see what was shared and "
                 "with whom, and to withdraw consent. Consent names the recipient and the categories of information.",
                 "A bank must share the information in the common data format that the regulator publishes with this "
                 "circular. It must not share it in another format.",
                 "A bank must run a dispute process for sharing that is wrong, not authorised or not what the customer "
                 "asked for. It must acknowledge a dispute within two working days and decide it within 20 working days.",
                 "A bank must keep a record of every sharing request and its outcome for five years.",
                 f"This circular takes effect on {eff(3, 180)}."], today),
    ]
    return {p["publication_id"]: p for p in pubs}


# Four publications that arrive one at a time through POST /admin/simulate/regulator-publication.
POOL = [
    ("circular", "Circular 2026/10: Records of sharing arrangements for customer information",
     "A bank must keep a record of each arrangement under which it shares customer information.",
     ["A bank must keep a record of each arrangement under which it shares customer information with a third party.",
      "The record must show the recipient, the categories of information, the purpose and the legal basis."]),
    ("circular", "Circular 2026/11: Telling customers when AI was used in a decision about them",
     "A bank must tell a customer when artificial intelligence was used in a decision about them.",
     ["A bank must tell a customer, in plain language, when artificial intelligence was used in a decision about the "
      "customer.",
      "The notice must say how the customer can ask for a person to look at the decision again."]),
    ("notice", "Notice 2026/12: Holiday opening hours of the regulator's counters",
     "The regulator's public counters close early on two days next month.",
     ["The regulator's public counters close at 13:00 on the two public holiday eves next month.",
      "Documents can still be filed through the regulator's website on those days."]),
    ("guideline", "Guideline 2026/06: Recovery time for critical systems",
     "A bank must set a recovery time of no more than four hours for each critical system and test it yearly.",
     ["A bank must set a recovery time objective of no more than four hours for each critical system.",
      "A bank must test the recovery plan for each critical system at least once a year."]),
]


def sim_publication(d: dict, today: date, n: int, seq: int) -> tuple[str, str]:
    """Add one publication from the pool. n picks the template, seq numbers the id."""
    kind, title, summary, paras = POOL[n % len(POOL)]
    pid = f"MFCA-2026-{seq:03d}"
    paras = list(paras) + [f"This publication takes effect on {long_date(today + timedelta(days=60))}."]
    d["regulator_publications"][pid] = {"publication_id": pid, "kind": kind, "published": today.isoformat(),
                                        "title": title, "summary": summary, "binding": True, "paragraphs": paras}
    return pid, (f"The {REGULATOR_NAME} has published {pid}: {title}. Read it on the regulator's website feed and compare it "
                 f"with the bank's policies.")
