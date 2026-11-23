"""Builds the whole starting data set. Same bank date and seed give the same data."""

from __future__ import annotations

import random
from datetime import date

from .config import SEED
from .seed_base import (build_accounts, build_background_transactions, build_banks, build_customers,
                        finalise_balances)
from .seed_fraud import build_fraud
from .seed_lend import POLICY, build_applications, build_approved_loan
from .seed_news import build_news
from .seed_recon import RULES as RECON_RULES, build_recon
from .seed_reg import build_publications
from .seed_pay import PURPOSE_CODES, RULES, build_payments
from .seed_scen1 import (add_ids, build_aml, build_cards, build_contacts, build_loans_and_exposure,
                         build_screening)


def build_all(today: date) -> dict:
    rng = random.Random(SEED)
    customers = build_customers(today)
    add_ids(customers)
    accounts = build_accounts(customers, rng, today)
    tb = build_background_transactions(customers, accounts, rng, today)
    contacts = build_contacts(customers, today)
    loans, exposure = build_loans_and_exposure(customers, today)
    cards, card_txns, disputes = build_cards(customers, accounts, today)
    watchlist, scr_alerts = build_screening(customers, today)
    aml_rules, counterparties, tma_alerts, cases, _ = build_aml(customers, accounts, tb, today)
    payments, investigations, repairs = build_payments(customers, accounts, tb, rng, today)
    applications, app_docs = build_applications(customers, today)
    approved_terms, loan_docs = build_approved_loan(today)
    fraud_rules, fraud_cases = build_fraud(customers, accounts, cards, card_txns, payments, contacts, tb, today)
    recon_accounts, recon_ledger, recon_statement, recon_breaks = build_recon(today)
    finalise_balances(accounts, tb.rows, rng)
    return {
        "banks": build_banks(), "customers": customers, "accounts": accounts, "transactions": tb.rows,
        "contacts": contacts, "loans": loans, "exposure": exposure, "cards": cards, "card_transactions": card_txns,
        "disputes": disputes, "card_replacements": {}, "watchlist": watchlist, "screening_alerts": scr_alerts,
        "aml_rules": aml_rules, "counterparties": counterparties, "monitoring_alerts": tma_alerts, "cases": cases,
        "payments": payments, "investigations": investigations, "repairs": repairs, "payment_rules": RULES,
        "purpose_codes": PURPOSE_CODES, "applications": applications, "application_docs": app_docs,
        "approved_terms": approved_terms, "loan_docs": loan_docs, "credit_policy": POLICY,
        "document_differences": {},
        "fraud_rules": fraud_rules, "fraud_cases": fraud_cases,
        "recon_accounts": recon_accounts, "recon_rules": RECON_RULES, "recon_ledger": recon_ledger,
        "recon_statement": recon_statement, "recon_breaks": recon_breaks,
        "news_articles": build_news(today), "media_screenings": {},
        "regulator_publications": build_publications(today),
    }
