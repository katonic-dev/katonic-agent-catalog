"""Seed data, part 9: records an auditor reads to test controls of policy MTB-POL-033 (tickets, changes, access reviews, recovery tests)."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from .seed_base import d_ago

POLICY_ID = "MTB-POL-033"
POLICY_TITLE = "Technology risk and outsourcing"
CRITICAL = ["core-banking", "payments-hub", "card-platform", "online-banking"]
ACCESS_SCOPE = ["core-banking", "payments-hub", "card-platform"]

CLAUSES = {
    "2.2": "Every critical system has a named owner, a recovery time objective and a tested recovery plan. Recovery is tested at least once a year.",
    "3.1": "A change to a critical system goes through change control, with a rollback plan and a named approver.",
    "6.1": "Access to systems follows least privilege and is reviewed quarterly.",
    "6.2": "Multi-factor authentication is required for every staff account that reaches a critical system.",
}


def months_back(d: date, n: int) -> date:
    m = d.month - n
    y = d.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def last_quarters(today: date, n: int = 4) -> list[tuple[int, int]]:
    y, q = today.year, (today.month - 1) // 3 + 1
    out = []
    for _ in range(n):
        q -= 1
        if q == 0:
            q, y = 4, y - 1
        out.append((y, q))
    return list(reversed(out))


def quarter_end(y: int, q: int) -> date:
    m = 3 * q
    return date(y, m, calendar.monthrange(y, m)[1])


def quarter_start(y: int, q: int) -> date:
    return date(y, 3 * q - 2, 1)


def label(yq: tuple[int, int]) -> str:
    return f"{yq[0]}-Q{yq[1]}"


def build_audit(today: date) -> dict:
    qs = last_quarters(today)
    missing_q = qs[2]
    tickets: dict = {}
    changes: dict = {}
    reviews: dict = {}
    recoveries: dict = {}
    tn = [3000]

    def ticket(system, typ, title, ago, desc, by, to, status="closed", change="", comment=""):
        tn[0] += 1
        tid = f"TKT-{tn[0]}"
        opened = d_ago(today, ago)
        tickets[tid] = {"ticket_id": tid, "system": system, "type": typ, "title": title, "opened": opened,
                        "closed": opened if status == "closed" else "", "status": status, "raised_by": by, "assigned_to": to,
                        "description": desc, "related_change_id": change, "comments": [comment] if comment else []}
        return tid

    # ---------------------------------------------------------------- access reviews (clause 6.1 and 6.2)
    owners = {"core-banking": "Lucan Pettigrew", "payments-hub": "Marisol Fenwick-Dray", "card-platform": "Tobias Ashgrove",
              "online-banking": "Ines Calloway-Rook"}
    exempt = {"payments-hub": ("svc-recon-batch", "service account that runs the nightly reconciliation batch"),
              "card-platform": ("svc-card-feed", "service account that sends the card file to the processor")}
    exempt_ticket = {}
    for system, (acct, why) in exempt.items():
        exempt_ticket[system] = ticket(
            system, "exemption", f"Exempt {acct} from multi-factor sign-in",
            200 if system == "payments-hub" else 185,
            f"Request to exempt the {why} ({acct}) from multi-factor sign-in because the job signs in without a person and cannot answer a "
            f"second factor. Compensating control proposed: the account can only sign in from one named server, and its password is kept in "
            f"the vault. Approved by the Head of Information Security. No end date was set.",
            owners[system], "Information Security", comment="Approved. Review again when the vendor supports certificate sign-in.")
    n = 1000
    for system in ACCESS_SCOPE:
        for yq in qs:
            if system == "payments-hub" and yq == missing_q:
                continue
            n += 1
            rid = f"ACR-{n}"
            total = {"core-banking": 142, "payments-hub": 96, "card-platform": 71}[system] + yq[1]
            ex = []
            if system in exempt and yq in qs[2:]:
                acct, _ = exempt[system]
                ex = [{"account_id": acct, "account_type": "service account", "ticket_id": exempt_ticket[system]}]
            reviews[rid] = {
                "review_id": rid, "system": system, "quarter": label(yq),
                "completed_on": (quarter_end(*yq) + timedelta(days=12 + (n % 5))).isoformat(), "reviewer": owners[system],
                "signed_off_by": "Head of Information Security", "staff_accounts_reviewed": total,
                "access_removed": 3 + n % 4, "staff_accounts_with_mfa": total - len(ex), "mfa_exemptions": ex,
                "notes": "Leavers and movers checked against the HR list. Privileged access confirmed with each manager."}
    ticket("payments-hub", "task", f"Access review for the payments hub, {label(missing_q)}, postponed", 140,
           "The quarterly access review for the payments hub is postponed because the system owner is on leave. It will be done when the "
           "owner returns. No new date was recorded.", "Marisol Fenwick-Dray", "Information Security", status="closed",
           comment="Closed as postponed. No review record was attached.")

    # ---------------------------------------------------------------- changes (clause 3.1)
    cn = [2200]

    def change(system, title, typ, ago, requester, approver, rollback, desc, status="implemented"):
        cn[0] += 1
        cid = f"CHG-{cn[0]}"
        tk = ticket(system, "change", f"Change request: {title}", ago + 5, desc, requester, "Change management", change=cid)
        changes[cid] = {"change_id": cid, "system": system, "title": title, "type": typ, "critical_system": system in CRITICAL,
                        "requested_by": requester, "approver": approver, "rollback_plan": rollback,
                        "implemented_on": d_ago(today, ago), "status": status, "ticket_id": tk, "description": desc,
                        "tested_before_release": True}
        return cid

    change("core-banking", "Apply the quarterly vendor patch to the core ledger", "normal", 150, "Lucan Pettigrew",
           "Hartley Winterbourne, Chief Information Officer",
           "Restore the ledger database from the pre-change snapshot and redeploy the previous release. Tested in the pre-production copy.",
           "Quarterly vendor patch. Applied in the Saturday window after testing in the pre-production copy.")
    change("payments-hub", "Release 8.4 of the payments hub", "normal", 120, "Marisol Fenwick-Dray",
           "Hartley Winterbourne, Chief Information Officer",
           "Redeploy release 8.3 from the artefact store. The database changes are reversible with the supplied script.",
           "New release with changes to the repair queue screens and two new payment rules.")
    change("card-platform", "Raise the contactless limit setting on the card platform", "normal", 90, "Tobias Ashgrove",
           "Hartley Winterbourne, Chief Information Officer", "",
           "One setting changed in the card platform configuration. The change request has no rollback section.")
    change("online-banking", "Renew the web certificate for online banking", "emergency", 60, "Ines Calloway-Rook", "",
           "Reinstall the previous certificate from the vault.",
           "The certificate was about to expire. Renewed out of hours as an emergency change. Approval was to be recorded afterwards.")
    change("core-banking", "Add an index to the transactions table", "normal", 35, "Lucan Pettigrew",
           "Hartley Winterbourne, Chief Information Officer",
           "Drop the index. Takes about a minute and does not affect data.", "Index added to speed up the month-end statement run.")
    # changes that are not in the sample
    change("payments-hub", "Update the bank directory file", "standard", 75, "Marisol Fenwick-Dray",
           "Hartley Winterbourne, Chief Information Officer", "Reload the previous directory file.", "Monthly directory update.")
    change("card-platform", "Rotate the keys used to sign the card file", "standard", 45, "Tobias Ashgrove",
           "Hartley Winterbourne, Chief Information Officer", "Revert to the previous key pair held in the vault.", "Yearly key rotation.")
    change("staff-intranet", "Change the colour scheme of the staff intranet", "standard", 30, "Ines Calloway-Rook",
           "Hartley Winterbourne, Chief Information Officer", "", "A cosmetic change. The intranet is not a critical system.")
    ticket("online-banking", "task", "Approval for the emergency certificate change", 59,
           "The emergency certificate renewal was done out of hours and the approver was not reached. The approval is to be recorded afterwards.",
           "Ines Calloway-Rook", "Change management", status="open", comment="No approval has been recorded yet.")

    # ---------------------------------------------------------------- recovery tests (clause 2.2)
    rn = [4000]

    def recovery(system, ago_days, scenario, achieved, result, finding="", date_override=None):
        rn[0] += 1
        rid = f"RCV-{rn[0]}"
        when = date_override or d_ago(today, ago_days)
        recoveries[rid] = {"recovery_test_id": rid, "system": system, "test_date": when, "scenario": scenario, "rto_target_hours": 4,
                           "rto_achieved_hours": achieved, "result": result, "tested_by": owners[system],
                           "report_reference": f"DR-{when[:4]}-{rn[0] - 4000:02d}", "findings": finding}

    recovery("core-banking", 520, "Failover of the core ledger to the second site", 3.5, "passed")
    recovery("core-banking", 150, "Failover of the core ledger to the second site", 3.0, "passed")
    recovery("payments-hub", 560, "Restore the payments hub from backup in the recovery site", 3.8, "passed")
    recovery("payments-hub", 210, "Restore the payments hub from backup in the recovery site", 4.5, "passed with findings",
             "Recovery took 4.5 hours against the 4 hour target. A runbook step was out of date.")
    recovery("online-banking", 500, "Rebuild the web tier in the recovery site", 2.5, "passed")
    recovery("online-banking", 95, "Rebuild the web tier in the recovery site", 2.2, "passed")
    recovery("card-platform", 0, "Restore the card platform from backup in the recovery site", 3.9, "passed", date_override=d_ago(today, 800))
    recovery("card-platform", 0, "Restore the card platform from backup in the recovery site", 3.6, "passed",
             date_override=months_back(today, 14).isoformat())
    ticket("card-platform", "task", "Recovery test for the card platform moved again", 270,
           "The yearly recovery test of the card platform was moved because of a release freeze. A new date was not set.",
           "Tobias Ashgrove", "Technology risk", comment="Closed with no new date.")

    # ---------------------------------------------------------------- a few more tickets, for noise and context
    ticket("core-banking", "incident", "Month-end statement run finished late", 52,
           "The month-end statement run finished two hours late because of a slow query. No customer was affected.", "Operations",
           "Lucan Pettigrew", comment="Fixed by the index change.")
    ticket("online-banking", "incident", "Login page slow for ten minutes", 40,
           "The login page answered slowly for ten minutes in the evening. Cause: a burst of requests from one network.", "Operations",
           "Ines Calloway-Rook")
    ticket("payments-hub", "access request", "Read-only access for a new analyst", 33,
           "Read-only access to the repair queue for a new analyst. Approved by the line manager.", "Marisol Fenwick-Dray", "Information Security")
    ticket("card-platform", "access request", "Remove access for a leaver", 28,
           "Access removed on the leaver's last day, as the HR list showed.", "Tobias Ashgrove", "Information Security")
    ticket("online-banking", "task", "Review of multi-factor sign-in settings", 21,
           "Annual look at the multi-factor settings for staff accounts. All staff accounts of online banking use multi-factor sign-in.",
           "Information Security", "Ines Calloway-Rook")

    def item(no, text, rtype, where):
        return {"item_no": no, "item": text, "record_type": rtype, "where_to_look": where}

    tests: dict = {}

    def test(tid, title, clause, objective, steps, plan, systems, pfrom, pto):
        tests[tid] = {"test_id": tid, "title": title, "policy_id": POLICY_ID, "policy_title": POLICY_TITLE, "clause": clause,
                      "clause_text": CLAUSES[clause], "control_objective": objective, "steps": steps, "evidence_plan": plan,
                      "systems_in_scope": systems, "period_from": pfrom, "period_to": pto, "status": "open", "evidence_packs": []}

    # CTL-1001: access reviewed quarterly
    plan = []
    for system in ACCESS_SCOPE:
        for yq in qs:
            plan.append(item(len(plan) + 1, f"Access review of {system} for {label(yq)}", "access_review",
                             f"list_access_reviews with system={system} and quarter={label(yq)}; one call with no filter returns the reviews of every item in this plan"))
    test("CTL-1001", "Access to critical systems is reviewed every quarter", "6.1",
         "Show that access to each critical system in scope was reviewed in each of the last four completed quarters.",
         ["List the access reviews for each system in scope.", "For each system and each quarter, find the review record and note who signed it off and when.",
          "Where a record is missing, search the tickets for an explanation and list what was searched.", "Do not conclude. Report what was found, what is missing and any exception."],
         plan, ACCESS_SCOPE, quarter_start(*qs[0]).isoformat(), quarter_end(*qs[-1]).isoformat())
    # CTL-1002: change control
    sample = ["CHG-2201", "CHG-2202", "CHG-2203", "CHG-2204", "CHG-2205"]
    plan = [item(i + 1, f"Change record {c} with a rollback plan and a named approver", "change_record",
                 f"get_change_record for {c}; its ticket is {changes[c]['ticket_id']}; one call of list_change_records with change_ids={','.join(sample)} "
                 f"returns every change in this plan in full") for i, c in enumerate(sample)]
    test("CTL-1002", "Changes to critical systems have a rollback plan and a named approver", "3.1",
         "Show that each sampled change to a critical system went through change control with a rollback plan and a named approver.",
         ["Take the five changes sampled for this test.", "Read each change record. Note the rollback plan and the approver.",
          "Read the ticket linked to the change for any context.", "Report any change where the rollback plan or the approver is missing. Do not conclude."],
         plan, sorted({changes[c]["system"] for c in sample}), d_ago(today, 160), today.isoformat())
    # CTL-1003: recovery tested yearly
    plan = [item(i + 1, f"Latest recovery test of {s}, dated within the 12 months before the bank date", "recovery_test",
                 f"list_recovery_tests with system={s}; one call with no filter returns the tests of every item in this plan") for i, s in enumerate(CRITICAL)]
    test("CTL-1003", "Recovery of each critical system is tested at least once a year", "2.2",
         "Show that each critical system has a recovery test dated within the last 12 months.",
         ["List the recovery tests for each critical system.", "Find the most recent test of each and note its date, result and recovery time against the target.",
          "Where the latest test is older than 12 months, search the tickets for a reason and list what was searched.", "Do not conclude."],
         plan, CRITICAL, months_back(today, 12).isoformat(), today.isoformat())
    # CTL-1004: multi-factor sign-in
    plan = [item(i + 1, f"Latest access review of {s} showing the multi-factor status of staff accounts", "access_review",
                 f"list_access_reviews with system={s}, newest quarter; one call with no filter returns the reviews of every item in this plan, "
                 f"with the exemptions") for i, s in enumerate(ACCESS_SCOPE)]
    plan.append(item(len(plan) + 1, "Any exemption from multi-factor sign-in, with the ticket that approved it", "ticket",
                     "search_tickets with text 'multi-factor'"))
    test("CTL-1004", "Staff accounts that reach critical systems use multi-factor sign-in", "6.2",
         "Show that every staff account that reaches a critical system in scope uses multi-factor sign-in, and list any account that does not.",
         ["Read the latest access review of each system in scope and note the staff accounts with and without multi-factor sign-in.",
          "For each account without it, find the ticket that approved the exemption.", "Report each exemption as an exception. Do not conclude."],
         plan, ACCESS_SCOPE, quarter_start(*qs[-1]).isoformat(), today.isoformat())
    return {"control_tests": tests, "tickets": tickets, "change_records": changes, "access_reviews": reviews,
            "recovery_tests": recoveries}
