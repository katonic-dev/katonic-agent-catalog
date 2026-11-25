"""Seed data, part 4: lending policy, applications, documents, approved loan."""

from __future__ import annotations

from datetime import date

from .seed_base import d_ago

PERSONAL_DOCS = [
    ("identity_document", "Identity document"),
    ("payslips_3_months", "Payslips, last three months"),
    ("bank_statements_3_months", "Bank statements, last three months"),
    ("employment_letter", "Employment letter"),
]
BUSINESS_DOCS = [
    ("company_registration", "Company registration certificate"),
    ("financial_statements", "Financial statements (latest year, or three years for loans over USD 100,000)"),
    ("bank_statements_6_months", "Business bank statements, last six months"),
    ("tax_return", "Latest tax return"),
    ("ownership_declaration", "Declaration of ultimate owners"),
    ("directors_identity", "Identity documents of the directors"),
]

POLICY = {
    "products": {
        "personal_loan": {"policy_id": "MTB-POL-030", "title": "Retail unsecured lending policy",
                          "required_documents": [{"type": t, "label": l} for t, l in PERSONAL_DOCS],
                          "ratios": [{"name": "debt_to_income", "definition":
                                      "(existing monthly debt payments + new monthly instalment) divided by gross monthly income",
                                      "threshold": "at most 0.40", "limit": 0.40, "direction": "max"}]},
        "business_loan_small": {"policy_id": "MTB-POL-031", "title": "Small business lending policy",
                                "required_documents": [{"type": t, "label": l} for t, l in BUSINESS_DOCS],
                                "ratios": [
                                    {"name": "current_ratio", "definition": "current assets divided by current liabilities, latest year",
                                     "threshold": "at least 1.20", "limit": 1.20, "direction": "min"},
                                    {"name": "debt_to_equity", "definition":
                                     "interest-bearing debt (long-term debt plus current portion) divided by total equity, latest year",
                                     "threshold": "at most 2.50", "limit": 2.50, "direction": "max"},
                                    {"name": "debt_service_cover", "definition":
                                     "EBITDA divided by (interest expense + scheduled principal repayments due in the next year), latest year",
                                     "threshold": "at least 1.25", "limit": 1.25, "direction": "min"}]},
    },
    "notes": "Figures in the application form must agree with the documents. When they do not, record both figures and the source of each.",
}


def installment(principal: float, apr_pct: float, months: int) -> float:
    r = apr_pct / 100 / 12
    return round(principal * r / (1 - (1 + r) ** -months), 2)



def build_applications(customers: dict, today: date):
    apps, docs = {}, {}
    # ---- LAP-8001 salaried personal loan, complete pack
    inst = installment(18000, 9.5, 36)
    apps["LAP-8001"] = {
        "application_id": "LAP-8001", "status": "received", "customer_id": "CUS-1012", "applicant": customers["CUS-1012"]["name"],
        "product": "personal_loan", "amount": 18000.0, "currency": "USD", "term_months": 36, "indicative_apr_pct": 9.5,
        "indicative_monthly_installment": inst, "purpose": "Kitchen and roof repairs at the applicant's home",
        "received": d_ago(today, 8),
        "form_fields": {"employer": "Westergate Water Board", "gross_monthly_income": 5200.0,
                        "existing_monthly_debt_payments": 450.0, "employment_start": "2016-04-01"},
        "missing_items_drafts": [], "credit_memo_drafts": []}
    docs["LAP-8001"] = {}
    for n, (t, title, text) in enumerate([
        ("identity_document", "National identity card (extract)",
         "IDENTITY CARD EXTRACT\nName: Marguerite Oakhaven\nDate of birth: 1988-02-16\nNationality: Meridia\n"
         "Number: " + customers["CUS-1012"]["id_number"] + "\nValid until: 2032-02-15"),
        ("payslips_3_months", "Payslips, last three months",
         "PAYSLIP SUMMARY. Employer: Westergate Water Board. Employee: Marguerite Oakhaven.\n"
         "Month        Gross     Tax      Pension   Net\n"
         "Month -1     5,200.00  780.00   410.00    4,010.00\n"
         "Month -2     5,200.00  780.00   410.00    4,010.00\n"
         "Month -3     5,200.00  780.00   410.00    4,010.00"),
        ("bank_statements_3_months", "Bank statement, last three months (extract)",
         "ACCOUNT STATEMENT ACC-1012-01 (extract)\nDate     Description                      Amount\n"
         "Month -3  Salary Westergate Water Board     +4,010.00\nMonth -3  Car loan instalment               -450.00\n"
         "Month -2  Salary Westergate Water Board     +4,010.00\nMonth -2  Car loan instalment               -450.00\n"
         "Month -1  Salary Westergate Water Board     +4,010.00\nMonth -1  Car loan instalment               -450.00\n"
         "Other spending averages 2,150.00 a month."),
        ("employment_letter", "Employment letter",
         "Westergate Water Board confirms that Marguerite Oakhaven has been employed full time, permanent contract, "
         "since 1 April 2016, with a gross monthly salary of USD 5,200.")], start=1):
        did = f"DOC-81{n:02d}"
        docs["LAP-8001"][did] = {"document_id": did, "application_id": "LAP-8001", "doc_type": t, "title": title,
                                 "received": d_ago(today, 8), "format": "extracted text", "text": text}

    # ---- LAP-8002 small business loan, two documents missing, one figure differs
    apps["LAP-8002"] = {
        "application_id": "LAP-8002", "status": "received", "customer_id": "CUS-1017",
        "applicant": customers["CUS-1017"]["name"], "product": "business_loan_small", "amount": 60000.0,
        "currency": "USD", "term_months": 48, "indicative_apr_pct": 10.5,
        "indicative_monthly_installment": installment(60000, 10.5, 48),
        "purpose": "Second delivery van and a cold-storage unit", "received": d_ago(today, 12),
        "form_fields": {"average_monthly_turnover": 62000.0, "annual_turnover": 744000.0, "employees": 11,
                        "years_trading": 9},
        "missing_items_drafts": [], "credit_memo_drafts": []}
    docs["LAP-8002"] = {}
    for n, (t, title, text) in enumerate([
        ("company_registration", "Company registration certificate (extract)",
         "Harrowgate Bakery Supplies Ltd. Registration number " + customers["CUS-1017"]["registration_number"] +
         ". Registered in Meridia. Incorporated 9 years ago. Status: active."),
        ("financial_statements", "Financial statements, latest year (summary)",
         "HARROWGATE BAKERY SUPPLIES LTD, latest financial year\nRevenue 612,000\nGross profit 171,000\nEBITDA 64,000\n"
         "Net profit 38,500\nTotal assets 340,000\nTotal equity 142,000"),
        ("bank_statements_6_months", "Business bank statements, six months (monthly totals)",
         "ACCOUNT ACC-1017-01, monthly totals\nMonth    Credits      Debits\nMonth -6  49,800.00   47,950.00\n"
         "Month -5  53,200.00   50,400.00\nMonth -4  47,100.00   46,820.00\nMonth -3  55,600.00   52,310.00\n"
         "Month -2  50,300.00   49,120.00\nMonth -1  52,400.00   50,010.00\nTotal credits 308,400.00"),
        ("directors_identity", "Identity documents of the directors (extract)",
         "Director 1: Ottoline Harrowgate, ID extract on file, valid. Director 2: Barnaby Harrowgate, ID extract on file, valid.")],
            start=1):
        did = f"DOC-82{n:02d}"
        docs["LAP-8002"][did] = {"document_id": did, "application_id": "LAP-8002", "doc_type": t, "title": title,
                                 "received": d_ago(today, 11), "format": "extracted text", "text": text}

    # ---- LAP-8003 small business loan with three years of financial statements
    apps["LAP-8003"] = {
        "application_id": "LAP-8003", "status": "received", "customer_id": "CUS-1018",
        "applicant": customers["CUS-1018"]["name"], "product": "business_loan_small", "amount": 120000.0,
        "currency": "USD", "term_months": 60, "indicative_apr_pct": 9.0,
        "indicative_monthly_installment": installment(120000, 9.0, 60),
        "purpose": "Replace two CNC machines", "received": d_ago(today, 15),
        "form_fields": {"average_monthly_turnover": 136667.0, "annual_turnover": 1640000.0, "employees": 24,
                        "years_trading": 17},
        "missing_items_drafts": [], "credit_memo_drafts": []}
    fs = (
        "PINECREST TOOLING WORKS LTD. Financial statements, three years, USD\n\n"
        "INCOME STATEMENT            Year -2      Year -1      Latest year\n"
        "Revenue                     1,420,000    1,515,000    1,640,000\n"
        "Cost of sales                 880,000      940,000    1,010,000\n"
        "Gross profit                  540,000      575,000      630,000\n"
        "Operating expenses            330,000      345,000      372,000\n"
        "EBITDA                        210,000      230,000      258,000\n"
        "Depreciation                   62,000       66,000       70,000\n"
        "EBIT                          148,000      164,000      188,000\n"
        "Interest expense               21,000       19,500       18,000\n"
        "Profit before tax             127,000      144,500      170,000\n"
        "Tax (25 percent)               31,750       36,125       42,500\n"
        "Net income                     95,250      108,375      127,500\n"
        "Dividends paid                      0       13,375       15,000\n\n"
        "BALANCE SHEET (year end)    Year -2      Year -1      Latest year\n"
        "Cash                           90,000      110,000      135,000\n"
        "Trade receivables             190,000      205,000      225,000\n"
        "Inventory                     130,000      140,000      145,000\n"
        "Total current assets          410,000      455,000      505,000\n"
        "Non-current assets (net)      620,000      640,000      664,500\n"
        "Total assets                1,030,000    1,095,000    1,169,500\n"
        "Trade payables                180,000      200,000      215,000\n"
        "Current portion of long-term debt 60,000      60,000       60,000\n"
        "Accruals                       60,000       70,000       77,000\n"
        "Total current liabilities     300,000      330,000      352,000\n"
        "Long-term debt                240,000      180,000      120,000\n"
        "Total liabilities             540,000      510,000      472,000\n"
        "Total equity                  490,000      585,000      697,500\n"
    )
    docs["LAP-8003"] = {}
    for n, (t, title, text) in enumerate([
        ("company_registration", "Company registration certificate (extract)",
         "Pinecrest Tooling Works Ltd. Registration number " + customers["CUS-1018"]["registration_number"] +
         ". Registered in Meridia. Status: active."),
        ("financial_statements", "Financial statements, three years", fs),
        ("bank_statements_6_months", "Business bank statements, six months (monthly totals)",
         "ACCOUNT ACC-1018-01, monthly totals\nMonth    Credits        Debits\nMonth -6  131,200.00    127,400.00\n"
         "Month -5  140,900.00    133,050.00\nMonth -4  129,300.00    128,700.00\nMonth -3  142,400.00    136,900.00\n"
         "Month -2  138,100.00    131,250.00\nMonth -1  137,500.00    132,800.00"),
        ("tax_return", "Latest tax return (summary)", "Tax return, latest year. Taxable profit 170,000. Tax due 42,500. Paid in full."),
        ("ownership_declaration", "Declaration of ultimate owners",
         "Owners: Hildegard Pinecrest 60 percent, Matthias Pinecrest 40 percent. No other owner holds 5 percent or more."),
        ("directors_identity", "Identity documents of the directors (extract)",
         "Both directors: ID extract on file, valid.")], start=1):
        did = f"DOC-83{n:02d}"
        docs["LAP-8003"][did] = {"document_id": did, "application_id": "LAP-8003", "doc_type": t, "title": title,
                                 "received": d_ago(today, 14), "format": "extracted text", "text": text}
    return apps, docs


def build_approved_loan(today: date):
    approved = {
        "LN-9001": {"loan_id": "LN-9001", "approval_reference": "CC-2026-0417", "borrower": "Lanternfish Logistics Ltd",
                    "facility": "Term loan", "amount": 250000.0, "currency": "USD", "term_months": 60,
                    "rate": {"base": "Meridian base rate", "margin_pct": 3.25},
                    "repayment": "Monthly instalments of principal and interest",
                    "arrangement_fee_pct": 0.75, "early_repayment_fee_pct": 1.0,
                    "covenants": [{"name": "minimum debt service cover", "threshold": 1.30,
                                   "test": "annual, on audited accounts"},
                                  {"name": "maximum debt to equity", "threshold": 2.0, "test": "annual"}],
                    "security": "First-ranking charge over the five delivery vehicles listed in Schedule A.",
                    "governing_law": "Meridia"},
        # LN-9006: a small loan whose funds were already released. Its contract agrees with every approved term, and the
        # lending system refuses to save differences on it (409): the document check closed when the funds went out.
        "LN-9006": {"loan_id": "LN-9006", "approval_reference": "CC-2026-0352", "borrower": "Lanternfish Logistics Ltd",
                    "facility": "Term loan", "amount": 40000.0, "currency": "USD", "term_months": 24,
                    "rate": {"base": "Meridian base rate", "margin_pct": 2.75},
                    "repayment": "Monthly instalments of principal and interest",
                    "arrangement_fee_pct": 0.5, "early_repayment_fee_pct": 1.0,
                    "covenants": [],
                    "security": "Unsecured.",
                    "governing_law": "Meridia",
                    "funds_released_on": d_ago(today, 30)},
    }
    contract = (
        "FACILITY AGREEMENT LN-9001\nBetween Meridian Trust Bank (the Bank) and Lanternfish Logistics Ltd (the Borrower).\n\n"
        "1. Facility. The Bank lends USD 250,000 as a term loan.\n"
        "2. Term. 60 months from the drawdown date.\n"
        "3. Interest. The Borrower pays the Meridian base rate plus a margin of 3.75 percent a year.\n"
        "4. Repayment. Monthly instalments of principal and interest.\n"
        "5. Fees. Arrangement fee 0.75 percent of the amount. Early repayment fee 1.0 percent of the amount repaid early.\n"
        "6. Financial covenants. (a) The debt service cover ratio must be at least 1.50, tested once a year on audited "
        "accounts. (b) Debt to equity must not exceed 2.0, tested once a year.\n"
        "7. Security. The Bank holds a general charge over all present and future assets of the Borrower.\n"
        "8. Governing law. The law of Meridia.\n")
    schedule = (
        "SCHEDULE A. Vehicles\nFive delivery vehicles, registration marks LF-101 to LF-105, owned by the Borrower. "
        "Total appraised value USD 310,000.")
    resolution = ("BOARD RESOLUTION of Lanternfish Logistics Ltd approving the facility LN-9001 and authorising two "
                  "directors to sign the facility agreement.")
    loan_docs = {"LN-9001": {
        "DOC-9101": {"document_id": "DOC-9101", "loan_id": "LN-9001", "doc_type": "facility_agreement",
                     "title": "Facility agreement (signed)", "format": "extracted text", "text": contract},
        "DOC-9102": {"document_id": "DOC-9102", "loan_id": "LN-9001", "doc_type": "schedule",
                     "title": "Schedule A, vehicles", "format": "extracted text", "text": schedule},
        "DOC-9103": {"document_id": "DOC-9103", "loan_id": "LN-9001", "doc_type": "board_resolution",
                     "title": "Borrower board resolution", "format": "extracted text", "text": resolution}},
        "LN-9006": {
            "DOC-9601": {"document_id": "DOC-9601", "loan_id": "LN-9006", "doc_type": "facility_agreement",
                         "title": "Facility agreement (signed)", "format": "extracted text", "text": (
                             "FACILITY AGREEMENT LN-9006\nBetween Meridian Trust Bank (the Bank) and Lanternfish Logistics Ltd (the Borrower).\n\n"
                             "1. Facility. The Bank lends USD 40,000 as a term loan.\n"
                             "2. Term. 24 months from the drawdown date.\n"
                             "3. Interest. The Borrower pays the Meridian base rate plus a margin of 2.75 percent a year.\n"
                             "4. Repayment. Monthly instalments of principal and interest.\n"
                             "5. Fees. Arrangement fee 0.50 percent of the amount. Early repayment fee 1.0 percent of the amount repaid early.\n"
                             "6. Security. None. The facility is unsecured.\n"
                             "7. Governing law. The law of Meridia.\n")}}}
    return approved, loan_docs
