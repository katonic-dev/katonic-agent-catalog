"""Seed data, part 6: account opening applications and periodic customer reviews (KYC), with their documents."""

from __future__ import annotations

from datetime import date

from .seed_base import COUNTRIES, d_ago

MAX_ADDRESS_AGE_DAYS = 90
OWNERSHIP_THRESHOLD_PCT = 25

REQUIREMENTS = {
    "bank_rules": {
        "proof_of_address_max_age": "A proof of address must be dated within the last 3 months (90 days) on the day the application is read.",
        "ownership_threshold": "Every person who owns 25 percent or more of a business must be identified, and every owner that is itself "
                               "a company must be traced through its own owners to the people behind it.",
        "higher_risk_countries": "Kharnovia (QP) is on the bank's higher-risk list. An owner, director or customer in a higher-risk "
                                 "country needs enhanced checks and the risk rating high.",
        "screening": "Every applicant, and for a business every director and every owner of 25 percent or more, is screened against the "
                     "Meridia Consolidated Demonstration List (invented) with screen_name. A strong match is never opened by the "
                     "branch: it is referred to Compliance."},
    "kinds": {
        "individual": {
            "documents": [
                {"type": "identity_document", "label": "Identity document, valid, not expired",
                 "must_agree_with_form": ["full_name", "date_of_birth", "nationality", "id_number"]},
                {"type": "proof_of_address", "label": "Proof of address, dated within 3 months",
                 "must_agree_with_form": ["full_name", "address"]}],
            "checks": ["Screen the applicant's name, date of birth and nationality with screen_name.",
                       "Compare every field of the form with the identity document and the proof of address.",
                       "Check that the proof of address is dated within the last 3 months."]},
        "business": {
            "documents": [
                {"type": "company_registry_extract", "label": "Company registry extract, issued within the last 3 months",
                 "must_agree_with_form": ["company_name", "registration_number", "registered_address", "directors"]},
                {"type": "constitutional_documents", "label": "Constitutional documents (articles of association)",
                 "must_agree_with_form": ["company_name"]},
                {"type": "ownership_declaration", "label": "Ownership declaration signed by a director",
                 "must_agree_with_form": ["owners_declared"]}],
            "checks": ["Screen the company, every director on the registry extract and every owner of 25 percent or more.",
                       "Compare the directors on the registry extract with the directors on the form.",
                       "Build the ownership chain down to the people behind it. List every gap. Never fill a gap from memory or guess.",
                       "Check the registry extract is issued within the last 3 months."]}},
    "differences_that_matter": [
        "A different spelling of a name between the form and the identity document (even one letter). The bank cannot assume it is a typing error: ask the applicant.",
        "A different date of birth, nationality or identity number.",
        "A proof of address older than 3 months.",
        "A director on the registry extract who is not on the form.",
        "An owner of 25 percent or more who is a company with no document showing who stands behind it.",
        "A strong match to a watchlist entry."],
    "differences_that_do_not_matter": [
        "Capital letters, accents and the order of words in an address.",
        "A road written as Rd or a street as St.",
        "A middle name left off the form when the document shows the same first and last names."],
    "decisions": {
        "approve": "All documents are received and agree with the form, screening is clear, and every owner of 25 percent or more is identified.",
        "ask_applicant": "Something is missing, out of date or does not agree. Tell the applicant exactly what is needed.",
        "decline": "The bank will not open the account for a reason it can state.",
        "refer_to_compliance": "A strong watchlist match. This is a recommendation only. Compliance decides, and the branch says nothing to the applicant about the reason."}}


# ------------------------------------------------------------------ document texts

COUNTRY_CODE = {name: code for code, name in COUNTRIES.items()}


def identity_text(name, dob, nationality, number, issued, expires, place, scanned):
    code = COUNTRY_CODE[nationality]
    return (f"IDENTITY CARD EXTRACT (text read from the scanned card)\n"
            f"Issuing authority: Registry of Persons, {nationality} (invented)\nCard type: National identity card\n"
            f"Surname and given names: {name}\nDate of birth: {dob}\nPlace of birth: {place}\nNationality: {nationality}\n"
            f"Identity number: {number}\nDate of issue: {issued}\nDate of expiry: {expires}\n"
            f"Machine-readable line: ID{code}<<{name.upper().replace(' ', '<')}<<{number.replace('-', '')}<<<<\n"
            f"Scan quality: both sides were captured, nothing is cropped, the photograph is clear and the hologram strip is visible.\n"
            f"Checks run by the branch scanner: the number format is valid, the expiry date is in the future, the photograph is present "
            f"and no sign of alteration was found.\n"
            f"Note for the reader: the scanner reads the text as it is printed on the card. It does not compare the card with the "
            f"application form. Any difference between the card and the form is for the reviewer to find and report.\n"
            f"Scan taken at the account opening desk on {scanned}. The original card was shown to the officer and returned to the applicant.")


def address_text(name, address, kind, provider, bill_date, period, amount):
    money = (f"Amount for the period: USD {amount:.2f}\nPayment status: paid by direct debit.\n" if amount
             else "Balance and transactions: not copied, only the header page was kept.\n")
    return (f"PROOF OF ADDRESS (text extract of a {kind})\nProvider: {provider} (invented)\nAccount holder: {name}\n"
            f"Supply address: {address}\nDocument date: {bill_date}\nPeriod covered: {period}\n{money}"
            f"The document is addressed to the account holder by name at the address above. The name, the address and the date are "
            f"printed in the header of the first page, and the provider's reference number is printed in the footer.\n"
            f"Scan quality: one page, complete, no cropping. The text was read automatically. The reader does not judge how old the "
            f"document is. The document date above is the date to use when the bank checks its age.\n"
            f"The provider's name and logo are printed at the top of the page and the document carries a reference number. The page was scanned "
            f"in colour at normal resolution, and every line of the address could be read without difficulty.\n"
            f"Received with the application at the account opening desk. The original was shown to the officer and returned.")


def registry_text(company, number, address, incorporated, status, directors, shareholders, issued, activity):
    dirs = "\n".join(f"  {n}, {role}, appointed {when}" for n, role, when in directors)
    sh = "\n".join(f"  {n} ({kind}, {country}), {pct} percent of the shares" for n, kind, country, pct in shareholders)
    return (f"COMPANY REGISTRY EXTRACT\nRegistry: Meridia Companies Registry (invented)\nCompany name: {company}\n"
            f"Registration number: {number}\nStatus: {status}\nDate of incorporation: {incorporated}\nRegistered address: {address}\n"
            f"Main activity: {activity}\nShare capital: 10,000 ordinary shares of USD 1 each, fully paid\n"
            f"DIRECTORS AND OFFICERS RECORDED AT THE REGISTRY\n{dirs}\nSHAREHOLDERS RECORDED AT THE REGISTRY\n{sh}\n"
            f"Last annual return filed: {incorporated[:4]} onwards, all returns filed on time. No charges are registered against the company.\n"
            f"Extract issued on {issued}. The extract shows the position on that date only. The registry records the direct "
            f"shareholders of a company. It does not record who owns a shareholder that is itself a company.\n"
            f"Registry notes: the company has filed every document that is due. No insolvency notice, winding-up petition or strike-off notice is "
            f"recorded. The extract was ordered online and carries the registry's electronic stamp.")


def constitution_text(company, number, adopted, signers):
    return (f"ARTICLES OF ASSOCIATION (extract of the clauses the bank reads)\nCompany: {company}\nRegistration number: {number}\n"
            f"Adopted on: {adopted}\n"
            f"1. The name of the company is {company}.\n2. The company is a private company limited by shares. Its shares may not be "
            f"offered to the public.\n3. The objects of the company are those of a general trading business. The company may open "
            f"accounts with any bank and borrow money for its business.\n"
            f"4. The share capital is 10,000 ordinary shares of USD 1 each. Each share carries one vote.\n"
            f"5. The business of the company is managed by its directors. A director is appointed or removed by a decision of the "
            f"holders of more than half of the shares.\n"
            f"6. Authority to open and operate bank accounts: {signers}\n"
            f"7. A share may be transferred only with the written consent of the directors.\n"
            f"8. The company keeps a register of its shareholders at its registered address.\n"
            f"Certified as a true copy by the company secretary. The text above was read from the scan of the certified copy.")


def ownership_text(company, signed_by, role, signed_on, rows, note):
    lines = "\n".join(f"  {n}: {kind}, {country}, {pct} percent" for n, kind, country, pct in rows)
    return (f"OWNERSHIP DECLARATION\nCompany: {company}\nSigned by: {signed_by}, {role}\nDate signed: {signed_on}\n"
            f"I declare that the following hold the shares of the company, directly:\n{lines}\n{note}\n"
            f"I understand that the bank relies on this declaration, and that I must tell the bank within 30 days if any holding changes. "
            f"I have given every owner of 25 percent or more that I know of, and I confirm the percentages add up to 100.\n"
            f"Signature: present on the scan. The signature was not compared with any specimen. Scan received at the account opening desk.\n"
            f"The declaration was completed on the bank's standard form and signed with an officer present, who checked the signer's identity card. "
            f"The percentages are shares of the issued ordinary shares. The signer was told that a false declaration breaks the account terms. The bank asks for a new declaration at each periodic review.")


def _doc(app_id, n, doc_type, title, received, text, document_date, prefix="OND"):
    """document_date is the date the document itself carries (issued, dated or signed). The onboarding system adds its age in days
    at the bank's date when the document is read."""
    did = f"{prefix}-{app_id[4:]}-{n:02d}"
    return did, {"document_id": did, "application_id": app_id, "doc_type": doc_type, "title": title, "received": received,
                 "document_date": document_date, "format": "extracted text", "text": text}


# ------------------------------------------------------------------ applications

def _individual(today, app_id, ago, form, id_text_args, addr_args):
    app = {"application_id": app_id, "kind": "individual", "status": "received", "received": d_ago(today, ago),
           "channel": "branch", "product": "Everyday Current Account", "applicant": form["full_name"], "form": form,
           "files": [], "decision": None}
    docs = {}
    for n, (t, title, text, dated) in enumerate([
            ("identity_document", "National identity card (extract)", identity_text(*id_text_args), id_text_args[4]),
            ("proof_of_address", "Proof of address (extract)", address_text(*addr_args), addr_args[4])], start=1):
        did, doc = _doc(app_id, n, t, title, d_ago(today, ago), text, dated)
        docs[did] = doc
    return app, docs


def _business(today, app_id, ago, form, reg_args, art_args, own_args):
    app = {"application_id": app_id, "kind": "business", "status": "received", "received": d_ago(today, ago),
           "channel": "branch", "product": "Business Current Account", "applicant": form["company_name"], "form": form,
           "files": [], "decision": None}
    docs = {}
    for n, (t, title, text, dated) in enumerate([
            ("company_registry_extract", "Company registry extract", registry_text(*reg_args), reg_args[7]),
            ("constitutional_documents", "Articles of association (extract)", constitution_text(*art_args), art_args[2]),
            ("ownership_declaration", "Ownership declaration", ownership_text(*own_args), own_args[3])], start=1):
        did, doc = _doc(app_id, n, t, title, d_ago(today, ago), text, dated)
        docs[did] = doc
    return app, docs


def _ind_form(name, dob, nat, address, idn, occupation, employer, funds):
    return {"full_name": name, "date_of_birth": dob, "nationality": nat, "address": address, "id_number": idn,
            "occupation": occupation, "employer": employer, "source_of_funds": funds,
            "expected_monthly_credits_usd": 3200}


def build_onboarding(today: date) -> tuple[dict, dict]:
    apps, docs = {}, {}

    def put(pair):
        apps[pair[0]["application_id"]] = pair[0]
        docs[pair[0]["application_id"]] = pair[1]

    # ONB-1001: clean individual
    addr = "14 Wren Alley, Port Ilvane, Meridia"
    put(_individual(today, "ONB-1001", 3,
                    _ind_form("Odalys Merrowby", "1990-04-18", "Meridia", addr, "MID-612045", "Dental nurse",
                              "Stillwater Clinic", "Salary"),
                    ("Odalys Merrowby", "1990-04-18", "Meridia", "MID-612045", d_ago(today, 900), d_ago(today, -2700),
                     "Port Ilvane", d_ago(today, 3)),
                    ("Odalys Merrowby", addr, "electricity bill", "Port Ilvane Power and Light", d_ago(today, 26),
                     f"{d_ago(today, 56)} to {d_ago(today, 26)}", 61.40)))
    # ONB-1002: name spelled differently, proof of address five months old
    addr = "7 Cobble Row, Tallowby, Meridia"
    put(_individual(today, "ONB-1002", 2,
                    _ind_form("Isadora Fenimore", "1986-09-02", "Meridia", addr, "MID-618377", "Bookkeeper",
                              "Oakline Freight Co", "Salary"),
                    ("Isadora Fennimore", "1986-09-02", "Meridia", "MID-618377", d_ago(today, 1500), d_ago(today, -2100),
                     "Tallowby", d_ago(today, 2)),
                    ("Isadora Fennimore", addr, "water bill", "Tallowby Water Board", d_ago(today, 150),
                     f"{d_ago(today, 180)} to {d_ago(today, 150)}", 38.75)))
    # ONB-1003: strong match to watchlist entry WL-9001
    addr = "31 Saltpan Road, Marlow Reach, Meridia"
    put(_individual(today, "ONB-1003", 1,
                    _ind_form("Wynn Castellano", "1962-02-02", "Brevnia", addr, "BRV-559120", "Machinery dealer",
                              "Self-employed", "Business income"),
                    ("Wynn Castellano", "1962-02-02", "Brevnia", "BRV-559120", d_ago(today, 700), d_ago(today, -1500),
                     "Brandymoor", d_ago(today, 1)),
                    ("Wynn Castellano", addr, "gas bill", "Marlow Reach Gas Company", d_ago(today, 19),
                     f"{d_ago(today, 49)} to {d_ago(today, 19)}", 72.10)))
    # ONB-1004: company, one owner of 100 percent, complete papers
    co, num, addr = "Cobblegate Print Supplies Ltd", "XM-REG-912044", "Unit 9, Printers Yard, Tallowby, Meridia"
    form = {"company_name": co, "registration_number": num, "registered_address": addr, "country": "Meridia",
            "activity": "paper and printing supplies", "directors": ["Bertrand Ulverstone"],
            "owners_declared": [{"name": "Bertrand Ulverstone", "type": "person", "percent": 100, "country": "Meridia"}],
            "authorised_signatory": "Bertrand Ulverstone", "expected_annual_turnover_usd": 480000}
    put(_business(today, "ONB-1004", 4, form,
                  (co, num, addr, "2019-03-11", "Active", [("Bertrand Ulverstone", "director and secretary", "2019-03-11")],
                   [("Bertrand Ulverstone", "person", "Meridia", 100)], d_ago(today, 12), "paper and printing supplies"),
                  (co, num, "2019-03-11", "A single director may open and operate bank accounts for the company."),
                  (co, "Bertrand Ulverstone", "director", d_ago(today, 5),
                   [("Bertrand Ulverstone", "person", "Meridia", 100)], "There are no other holders.")))
    # ONB-1005: 60 percent held by a company in Quenmark, nothing shows who owns it
    co, num, addr = "Larkfield Marine Services Ltd", "XM-REG-912377", "Pier 3, Dock Road, Port Ilvane, Meridia"
    form = {"company_name": co, "registration_number": num, "registered_address": addr, "country": "Meridia",
            "activity": "boat repair and marine fuel", "directors": ["Corwin Ashdown"],
            "owners_declared": [
                {"name": "Vardane Holdings Ltd", "type": "company", "percent": 60, "country": "Quenmark"},
                {"name": "Corwin Ashdown", "type": "person", "percent": 40, "country": "Meridia"}],
            "authorised_signatory": "Corwin Ashdown", "expected_annual_turnover_usd": 910000,
            "note_on_form": "The holding company is in Quenmark. Our accountant keeps its records."}
    put(_business(today, "ONB-1005", 6, form,
                  (co, num, addr, "2017-08-22", "Active", [("Corwin Ashdown", "director and secretary", "2017-08-22")],
                   [("Vardane Holdings Ltd", "company", "Quenmark", 60), ("Corwin Ashdown", "person", "Meridia", 40)],
                   d_ago(today, 10), "boat repair and marine fuel"),
                  (co, num, "2017-08-22", "Any two persons named in the register of directors may open accounts. Where only one "
                                          "director is in office, that director may act alone."),
                  (co, "Corwin Ashdown", "director", d_ago(today, 7),
                   [("Vardane Holdings Ltd", "company", "Quenmark", 60), ("Corwin Ashdown", "person", "Meridia", 40)],
                   "Vardane Holdings Ltd is a company registered in Hartsfell, Quenmark.")))
    # ONB-1006: the registry shows a director the form does not list
    co, num, addr = "Thistlewick Bakehouse Ltd", "XM-REG-912566", "2 Oven Lane, Marlow Reach, Meridia"
    form = {"company_name": co, "registration_number": num, "registered_address": addr, "country": "Meridia",
            "activity": "bakery and cafe", "directors": ["Nerys Hallowfield"],
            "owners_declared": [{"name": "Nerys Hallowfield", "type": "person", "percent": 70, "country": "Meridia"},
                                {"name": "Garrick Oldacre", "type": "person", "percent": 30, "country": "Meridia"}],
            "authorised_signatory": "Nerys Hallowfield", "expected_annual_turnover_usd": 260000}
    put(_business(today, "ONB-1006", 5, form,
                  (co, num, addr, "2021-05-04", "Active",
                   [("Nerys Hallowfield", "director", "2021-05-04"), ("Garrick Oldacre", "director", d_ago(today, 21))],
                   [("Nerys Hallowfield", "person", "Meridia", 70), ("Garrick Oldacre", "person", "Meridia", 30)],
                   d_ago(today, 9), "bakery and cafe"),
                  (co, num, "2021-05-04", "Any one director may open and operate bank accounts for the company."),
                  (co, "Nerys Hallowfield", "director", d_ago(today, 6),
                   [("Nerys Hallowfield", "person", "Meridia", 70), ("Garrick Oldacre", "person", "Meridia", 30)],
                   "There are no other holders.")))
    return apps, docs


# ------------------------------------------------------------------ periodic reviews

def _days_between(earlier: str, later: str) -> int:
    return (date.fromisoformat(later) - date.fromisoformat(earlier)).days


def occupation_text(name, employer, role, since, income, signed_on, received):
    return (f"OCCUPATION LETTER (text extract)\nIssued by: {employer}\nAddressed to: Meridian Trust Bank, customer reviews\n"
            f"Subject: {name}\nThis letter confirms that {name} works for {employer} as {role}, since {since}.\n"
            f"Gross monthly pay: USD {income:,.2f}, paid into an account at Meridian Trust Bank.\n"
            f"The letter was signed on {signed_on} by the person responsible for payroll, whose name and telephone number are "
            f"printed under the signature. It is on the company's letterhead and carries the company stamp.\n"
            f"Scan quality: one page, complete. The text was read automatically. The reader does not check the claims in the letter "
            f"against any other record. The writer gave a telephone number for payroll questions. The letter is dated {signed_on}, "
            f"{_days_between(signed_on, received)} days before the bank received it on {received}. It names no other employer and no other "
            f"source of income.\nReceived by post as part of a periodic review of the customer.")


def self_employment_text(name, registry, role, since, income, signed_on, received):
    return (f"SELF-EMPLOYMENT REGISTRATION LETTER (text extract)\nIssued by: {registry}\nAddressed to: Meridian Trust Bank, customer reviews\n"
            f"Subject: {name}\nThis letter confirms that {name} is registered with {registry} as {role}, trading on their own account "
            f"since {since}. They have no employer.\n"
            f"Declared gross monthly business income: USD {income:,.2f}, paid into an account at Meridian Trust Bank.\n"
            f"The letter was signed on {signed_on} by a registration officer of the registry, whose name and telephone number are "
            f"printed under the signature. It is on the registry's letterhead and carries the registry's stamp.\n"
            f"Scan quality: one page, complete. The text was read automatically. The reader does not check the claims in the letter "
            f"against any other record. The officer gave a telephone number for questions about the registration. The letter is dated "
            f"{signed_on}, {_days_between(signed_on, received)} days before the bank received it on {received}. It names no employer and "
            f"no other source of income.\nReceived by post as part of a periodic review of the customer.")


def build_reviews(customers: dict, today: date) -> tuple[dict, dict]:
    reviews, docs = {}, {}

    def review(rid, cid, ago_last, due_ago, held, doc_specs):
        reviews[rid] = {"review_id": rid, "customer_id": cid, "status": "open", "review_reason": "periodic review",
                        "last_review_date": d_ago(today, ago_last), "due_date": d_ago(today, due_ago),
                        "risk_rating": customers[cid]["risk_rating"], "held_profile": held, "profile_drafts": [],
                        "completion": None}
        docs[rid] = {}
        for n, (t, title, text, dated) in enumerate(doc_specs, start=1):
            did = f"KYD-{rid[4:]}-{n:02d}"
            docs[rid][did] = {"document_id": did, "review_id": rid, "doc_type": t, "title": title,
                              "received": d_ago(today, 6), "document_date": dated, "format": "extracted text", "text": text}

    # KYR-1001: nothing has changed
    c = customers["CUS-1013"]
    held = {"name": c["name"], "date_of_birth": c["date_of_birth"], "nationality": "Meridia", "address": c["address"],
            "id_number": c["id_number"], "occupation": "Harbour pilot", "employer": "Tallowby Council Works",
            "source_of_funds": "Salary"}
    review("KYR-1001", "CUS-1013", 372, 8, held, [
        ("identity_document", "National identity card (extract)",
         identity_text(c["name"], c["date_of_birth"], "Meridia", c["id_number"], d_ago(today, 1200), d_ago(today, -2400),
                       "Port Ilvane", d_ago(today, 6)), d_ago(today, 1200)),
        ("proof_of_address", "Proof of address (extract)",
         address_text(c["name"], c["address"], "bank statement from another provider", "Harbourside Savings Union",
                      d_ago(today, 33), f"{d_ago(today, 63)} to {d_ago(today, 33)}", 0), d_ago(today, 33))])
    # KYR-1002: new address and occupation, same rating
    c = customers["CUS-1015"]
    new_addr = "22 Barley Mill Lane, Tallowby, Meridia"
    held = {"name": c["name"], "date_of_birth": c["date_of_birth"], "nationality": "Meridia", "address": c["address"],
            "id_number": c["id_number"], "occupation": "Quantity surveyor", "employer": "Ferrow Brothers Builders",
            "source_of_funds": "Salary"}
    review("KYR-1002", "CUS-1015", 380, 15, held, [
        ("proof_of_address", "Proof of address (extract)",
         address_text(c["name"], new_addr, "electricity bill", "Tallowby Power Company", d_ago(today, 14),
                      f"{d_ago(today, 44)} to {d_ago(today, 14)}", 88.20), d_ago(today, 14)),
        ("occupation_letter", "Self-employment registration letter (extract)",
         self_employment_text(c["name"], "Meridia Revenue Registry (invented)", "a self-employed building surveyor", d_ago(today, 160),
                              4800.0, d_ago(today, 10), d_ago(today, 6)), d_ago(today, 10))])
    # KYR-1003: a business with a new 30 percent owner in Kharnovia
    c = customers["CUS-1024"]
    held = {"name": c["name"], "registration_number": c["registration_number"], "address": c["address"],
            "activity": c["business_activity"], "directors": ["Ottoline Brackenridge", "Hamish Brackenridge"],
            "owners": [{"name": "Ottoline Brackenridge", "percent": 55, "country": "Meridia"},
                       {"name": "Hamish Brackenridge", "percent": 45, "country": "Meridia"}]}
    rows = [("Ottoline Brackenridge", "person", "Meridia", 40), ("Hamish Brackenridge", "person", "Meridia", 30),
            ("Tavish Orrelby", "person", "Kharnovia", 30)]
    review("KYR-1003", "CUS-1024", 390, 20, held, [
        ("company_registry_extract", "Company registry extract",
         registry_text(c["name"], c["registration_number"], c["address"], "2018-06-14", "Active",
                       [("Ottoline Brackenridge", "director", "2018-06-14"), ("Hamish Brackenridge", "director", "2018-06-14")],
                       rows, d_ago(today, 9), "dental clinics"), d_ago(today, 9)),
        ("ownership_declaration", "Ownership declaration",
         ownership_text(c["name"], "Ottoline Brackenridge", "director", d_ago(today, 7), rows,
                        "Tavish Orrelby bought his shares from the other two holders, and lives in Gallowmere, Kharnovia."), d_ago(today, 7))])
    return reviews, docs


# ------------------------------------------------------------------ simulated arrivals

def sim_application(d: dict, today: date, kind: int, n: int) -> tuple[str, str]:
    """One new application from four rotating templates. Returns the id and a plain sentence."""
    aid = f"ONB-{1100 + n}"
    if kind == 0:
        addr = f"{10 + n} Fennel Close, Port Ilvane, Meridia"
        form = _ind_form("Linnet Aldercott", "1993-01-25", "Meridia", addr, f"MID-62{n:04d}", "Teacher", "Westergate Water Board", "Salary")
        pair = _individual(today, aid, 0, form,
                           ("Linnet Aldercott", "1993-01-25", "Meridia", f"MID-62{n:04d}", d_ago(today, 400), d_ago(today, -3000),
                            "Port Ilvane", today.isoformat()),
                           ("Linnet Aldercott", addr, "electricity bill", "Port Ilvane Power and Light", d_ago(today, 20),
                            f"{d_ago(today, 50)} to {d_ago(today, 20)}", 55.00))
        text = "an individual with a complete pack"
    elif kind == 1:
        addr = f"{20 + n} Heron Steps, Marlow Reach, Meridia"
        form = _ind_form("Peregrine Tolliver", "1979-07-09", "Meridia", addr, f"MID-63{n:04d}", "Electrician", "Self-employed", "Business income")
        pair = _individual(today, aid, 0, form,
                           ("Peregrine Tolliver", "1979-07-09", "Meridia", f"MID-63{n:04d}", d_ago(today, 2300), d_ago(today, 20),
                            "Marlow Reach", today.isoformat()),
                           ("Peregrine Tolliver", addr, "gas bill", "Marlow Reach Gas Company", d_ago(today, 30),
                            f"{d_ago(today, 60)} to {d_ago(today, 30)}", 47.30))
        text = "an individual whose identity card expired 20 days ago"
    elif kind == 2:
        co, num, addr = f"Fernhollow Tyre Centre {n} Ltd", f"XM-REG-93{n:04d}", "Unit 2, Axle Road, Tallowby, Meridia"
        owner = "Quillon Ferris"
        form = {"company_name": co, "registration_number": num, "registered_address": addr, "country": "Meridia",
                "activity": "tyre fitting", "directors": [owner],
                "owners_declared": [{"name": owner, "type": "person", "percent": 100, "country": "Meridia"}],
                "authorised_signatory": owner, "expected_annual_turnover_usd": 310000}
        pair = _business(today, aid, 0, form,
                         (co, num, addr, "2020-02-17", "Active", [(owner, "director", "2020-02-17")],
                          [(owner, "person", "Meridia", 100)], d_ago(today, 5), "tyre fitting"),
                         (co, num, "2020-02-17", "A single director may open and operate bank accounts for the company."),
                         (co, owner, "director", d_ago(today, 2), [(owner, "person", "Meridia", 100)], "There are no other holders."))
        text = "a company with one owner of 100 percent and complete papers"
    else:
        co, num, addr = f"Brindlewood Cargo {n} Ltd", f"XM-REG-94{n:04d}", "Warehouse 11, Dock Road, Port Ilvane, Meridia"
        owner = "Ansel Vickery"
        form = {"company_name": co, "registration_number": num, "registered_address": addr, "country": "Meridia",
                "activity": "freight forwarding", "directors": [owner],
                "owners_declared": [{"name": "Torvald Holdings Ltd", "type": "company", "percent": 50, "country": "Rovaland"},
                                    {"name": owner, "type": "person", "percent": 50, "country": "Meridia"}],
                "authorised_signatory": owner, "expected_annual_turnover_usd": 740000}
        pair = _business(today, aid, 0, form,
                         (co, num, addr, "2018-10-30", "Active", [(owner, "director", "2018-10-30")],
                          [("Torvald Holdings Ltd", "company", "Rovaland", 50), (owner, "person", "Meridia", 50)],
                          d_ago(today, 6), "freight forwarding"),
                         (co, num, "2018-10-30", "A single director may open and operate bank accounts for the company."),
                         (co, owner, "director", d_ago(today, 3),
                          [("Torvald Holdings Ltd", "company", "Rovaland", 50), (owner, "person", "Meridia", 50)],
                          "Torvald Holdings Ltd is a company registered in Duskmere, Rovaland."))
        text = "a company half owned by a holding company in Rovaland whose own owners are not shown in any document"
    d["onb_applications"][aid] = pair[0]
    d["onb_documents"][aid] = pair[1]
    return aid, (f"A new account opening application {aid} has arrived in the onboarding system from {pair[0]['applicant']}: "
                 f"{text}. It is received and needs a file. Read it with get_onboarding_application in the onboarding system.")


def sim_review(d: dict, today: date, kind: int, n: int) -> tuple[str, str]:
    """One new periodic review from four rotating templates."""
    rid = f"KYR-{1100 + n}"
    cust = d["customers"]
    cid = ["CUS-1003", "CUS-1005", "CUS-1018", "CUS-1009"][kind]
    c = cust[cid]
    docs: dict = {}
    if c["type"] == "individual":
        held = {"name": c["name"], "date_of_birth": c["date_of_birth"], "nationality": c["nationality_name"], "address": c["address"],
                "id_number": c["id_number"], "occupation": "Office clerk", "employer": "Harbourlight Services", "source_of_funds": "Salary"}
    else:
        held = {"name": c["name"], "registration_number": c["registration_number"], "address": c["address"],
                "activity": c["business_activity"], "directors": ["Rowan Pellingham"],
                "owners": [{"name": "Rowan Pellingham", "percent": 100, "country": "Meridia"}]}
    fresh = []
    if kind == 0:
        fresh = [("proof_of_address", "Proof of address (extract)", address_text(c["name"], c["address"], "water bill", "Tallowby Water Board",
                                                                                    d_ago(today, 20), f"{d_ago(today, 50)} to {d_ago(today, 20)}", 34.10),
                  d_ago(today, 20))]
        text = "The documents received show the same address as the bank holds. Nothing has changed."
    elif kind == 1:
        fresh = [("proof_of_address", "Proof of address (extract)", address_text(c["name"], f"{40 + n} Plover Way, Port Ilvane, Meridia", "gas bill",
                                                                                    "Port Ilvane Gas Company", d_ago(today, 12),
                                                                                    f"{d_ago(today, 42)} to {d_ago(today, 12)}", 58.00),
                  d_ago(today, 12))]
        text = "A new proof of address shows a different address."
    elif kind == 2:
        rows = [("Rowan Pellingham", "person", "Meridia", 70), ("Idris Calloway", "person", "Kharnovia", 30)]
        fresh = [("ownership_declaration", "Ownership declaration",
                  ownership_text(c["name"], "Rowan Pellingham", "director", d_ago(today, 8), rows,
                                 "Idris Calloway bought 30 percent of the shares and lives in Gallowmere, Kharnovia."), d_ago(today, 8))]
        text = "A new ownership declaration shows a new owner of 30 percent who lives in Kharnovia."
    else:
        fresh = [("occupation_letter", "Occupation letter (extract)",
                  occupation_text(c["name"], "Quillon Software Ltd", "a support analyst", d_ago(today, 90), 3900.0, d_ago(today, 9),
                                  today.isoformat()), d_ago(today, 9))]
        text = "An occupation letter shows a new employer."
    for i, (t, title, body, dated) in enumerate(fresh, start=1):
        docs[f"KYD-{rid[4:]}-{i:02d}"] = {"document_id": f"KYD-{rid[4:]}-{i:02d}", "review_id": rid, "doc_type": t, "title": title,
                                           "received": today.isoformat(), "document_date": dated, "format": "extracted text", "text": body}
    d["kyc_reviews"][rid] = {"review_id": rid, "customer_id": cid, "status": "open", "review_reason": "periodic review",
                             "last_review_date": d_ago(today, 366), "due_date": today.isoformat(), "risk_rating": c["risk_rating"],
                             "held_profile": held, "profile_drafts": [], "completion": None}
    d["kyc_documents"][rid] = docs
    return rid, (f"A periodic review {rid} has arrived in the onboarding system for customer {cid} ({c['name']}). {text} "
                 f"It is open and needs a refreshed profile. Read it with get_kyc_review in the onboarding system.")
