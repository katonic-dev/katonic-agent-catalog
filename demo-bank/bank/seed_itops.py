"""Seed data, part 10: IT operations. Incidents, monitoring series, dashboards, changes and runbooks.

The service clock stands at 10:00 on the bank date. Times are local, written as YYYY-MM-DDTHH:MM.
Four incidents have fixed ids INC-7001 to INC-7004. SCENARIOS.md has the right answer for each.
"""

from __future__ import annotations

from datetime import date, timedelta

NOW_TIME = "10:00"
ON_CALL = {"payments": "Joran Pellmoor", "cards": "Ysolde Carraway-Finch", "platform": "Bram Ostenholt", "manager": "Nerys Quillon-Marsh"}

UNITS = {"error_rate_pct": "percent", "latency_p95_ms": "milliseconds", "volume_per_min": "per minute",
         "payments_db_cpu_pct": "percent", "volume_from_app_log_per_min": "per minute", "db_pool_in_use_pct": "percent",
         "queue_depth": "messages", "disk_used_pct": "percent"}
MEASURE_NOTES = {
    "error_rate_pct": "Share of requests that ended in a technical error.",
    "latency_p95_ms": "Time within which 95 percent of requests finished.",
    "volume_per_min": "Requests per minute as counted by the monitoring collector.",
    "payments_db_cpu_pct": "CPU use of the payments database host.",
    "volume_from_app_log_per_min": "Requests per minute counted from the service's own application log. It does not use the collector.",
    "db_pool_in_use_pct": "Share of database connections in use by the service.",
    "queue_depth": "Messages waiting in the service's queue.",
    "disk_used_pct": "Share of the disk in use.",
}


def day(today: date, ago: int) -> str:
    return (today - timedelta(days=ago)).isoformat()


def stamp(today: date, ago: int, hhmm: str) -> str:
    return f"{day(today, ago)}T{hhmm}"


def times(start: str, step: int, n: int) -> list[str]:
    h, m = int(start[:2]), int(start[3:])
    base = h * 60 + m
    return [f"{(base + i * step) // 60:02d}:{(base + i * step) % 60:02d}" for i in range(n)]


def points(today: date, ago: int, hhmms: list[str], values: list[float]) -> list[dict]:
    assert len(hhmms) == len(values)
    return [{"time": stamp(today, ago, t), "value": v} for t, v in zip(hhmms, values)]


def baseline(n: int, level: float, wobble: list[float]) -> list[float]:
    return [round(level + wobble[i % len(wobble)], 2) for i in range(n)]


def build_metrics(today: date) -> dict:
    m: dict = {}
    # ---- INC-7001: payment-service, 07:00 to 10:00 every 10 minutes (19 points)
    t = times("07:00", 10, 19)
    m["payment-service"] = {
        "latency_p95_ms": points(today, 0, t, [418, 422, 415, 430, 425, 419, 421, 428, 612, 1480, 2310, 2780, 2905, 3010, 2950, 3120, 3085, 3140, 3200]),
        "error_rate_pct": points(today, 0, t, [0.2, 0.2, 0.3, 0.2, 0.2, 0.3, 0.2, 0.2, 0.6, 1.4, 2.1, 2.4, 2.6, 2.5, 2.7, 2.6, 2.8, 2.7, 2.9]),
        "volume_per_min": points(today, 0, t, [208, 211, 206, 213, 209, 214, 210, 212, 209, 190, 171, 160, 158, 162, 157, 160, 155, 158, 156]),
        "payments_db_cpu_pct": points(today, 0, t, [34, 35, 33, 36, 34, 35, 34, 36, 52, 79, 88, 91, 92, 93, 92, 94, 93, 94, 95]),
    }
    # ---- INC-7002: card-authorisation, 04:00 to 10:00 every 20 minutes (19 points). The certificate expired at 04:58.
    t = times("04:00", 20, 19)
    m["card-authorisation"] = {
        "error_rate_pct": points(today, 0, t, [0.4, 0.5, 0.4] + [97.2, 97.8, 98.1, 97.9, 98.0, 97.6, 97.8, 98.2, 97.9, 97.7, 98.0, 97.8, 97.9, 98.1, 97.8, 97.9]),
        "latency_p95_ms": points(today, 0, t, [182, 179, 185] + [41, 39, 38, 40, 37, 38, 39, 38, 40, 39, 38, 37, 39, 38, 38, 39]),
        "volume_per_min": points(today, 0, t, [38, 36, 37] + [41, 45, 52, 60, 72, 85, 98, 110, 118, 121, 124, 126, 128, 127, 129, 130]),
    }
    # ---- INC-7003: statement-service, 08:00 to 10:00 every 10 minutes. The collector sent nothing from 09:10 to 09:40.
    t = times("08:00", 10, 13)
    with_gap = [x for x in t if x not in ("09:10", "09:20", "09:30", "09:40")]
    vol = {"08:00": 31, "08:10": 30, "08:20": 33, "08:30": 29, "08:40": 32, "08:50": 31, "09:00": 30, "09:50": 31, "10:00": 32}
    m["statement-service"] = {
        "volume_per_min": points(today, 0, with_gap, [vol[x] for x in with_gap]),
        "volume_from_app_log_per_min": points(today, 0, t, [31, 30, 33, 29, 32, 31, 30, 32, 31, 29, 30, 31, 32]),
        "error_rate_pct": points(today, 0, t, [0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.1, 0.2]),
        "latency_p95_ms": points(today, 0, t, [262, 258, 270, 255, 266, 261, 259, 264, 268, 257, 263, 260, 265]),
    }
    # ---- INC-7004: online-banking, nine days ago, 13:30 to 16:30 every 10 minutes (19 points)
    t = times("13:30", 10, 19)
    m["online-banking"] = {
        "error_rate_pct": points(today, 9, t, [0.3, 0.3, 0.4, 0.3, 18.5, 22.1, 23.4, 22.8, 23.0, 22.6, 23.1, 21.9, 1.2, 0.6, 0.4, 0.3, 0.3, 0.3, 0.3]),
        "latency_p95_ms": points(today, 9, t, [318, 322, 315, 320, 905, 1120, 1180, 1150, 1170, 1140, 1160, 1130, 420, 335, 322, 319, 321, 318, 320]),
        "volume_per_min": points(today, 9, t, [610, 625, 640, 650, 590, 560, 545, 550, 548, 552, 549, 553, 600, 630, 645, 652, 640, 630, 620]),
        "db_pool_in_use_pct": points(today, 9, t, [41, 40, 42, 41, 43, 42, 41, 40, 41, 42, 41, 40, 41, 42, 41, 40, 41, 40, 41]),
    }
    # ---- services that only appear in simulated incidents: a normal morning
    t = times("08:00", 10, 13)
    for svc, lat, vol_, extra in (("notification-service", 140, 85, ("queue_depth", 12)),
                                  ("ledger-posting", 310, 60, None),
                                  ("reporting-database", 520, 14, ("disk_used_pct", 61)),
                                  ("mobile-gateway", 210, 480, None)):
        m[svc] = {"error_rate_pct": points(today, 0, t, baseline(13, 0.2, [0.0, 0.1, -0.1, 0.05])),
                  "latency_p95_ms": points(today, 0, t, baseline(13, lat, [0, 4, -3, 2, -5])),
                  "volume_per_min": points(today, 0, t, baseline(13, vol_, [0, 2, -2, 1, -1]))}
        if extra:
            m[svc][extra[0]] = points(today, 0, t, baseline(13, extra[1], [0, 1, -1, 0]))
    return m


def build_changes(today: date) -> dict:
    ch = {}

    def add(cid, service, title, ago, hhmm, by, approver, typ, desc, scheduled="", note=""):
        ch[cid] = {"change_id": cid, "service": service, "title": title, "type": typ, "implemented_at": stamp(today, ago, hhmm),
                   "scheduled_for": scheduled or stamp(today, ago, hhmm), "implemented_by": by, "approved_by": approver,
                   "status": "completed", "description": desc, "note": note, "rollback_plan": "See the runbook of the service."}

    add("ITC-8101", "payment-service", "Release 4.18.0 of payment-service", 0, "08:00", "Joran Pellmoor", "Nerys Quillon-Marsh", "normal",
        "Deploys release 4.18.0 to all four nodes. The release adds a check that looks for a duplicate payment (same payer, payee, amount and "
        "reference in the last 24 hours) by querying the payments table. The check is behind the flag duplicate_check_enabled. The flag is "
        "switched on by the release schedule 15 minutes after the deploy, once the nodes report healthy. Previous release: 4.17.3.")
    add("ITC-8102", "notification-service", "Update the text of the payment receipt message", 0, "07:10", "Orlaith Brannock", "Nerys Quillon-Marsh",
        "standard", "Changes the wording of the receipt message sent after a payment. No code change. Does not touch the payment path.")
    add("ITC-8103", "reporting-database", "Rebuild three indexes on the reporting database", 1, "23:30", "Bram Ostenholt", "Nerys Quillon-Marsh",
        "standard", "Night maintenance on the reporting database. Separate from the payments database. Finished at 00:40.")
    add("ITC-8104", "card-authorisation", "Raise the declined-purchase threshold for the travel rule", 12, "11:15", "Ysolde Carraway-Finch",
        "Nerys Quillon-Marsh", "standard", "Configuration change to one authorisation rule. No certificate or network change.")
    add("ITC-8105", "statement-service", "Move the statement archive to the new storage tier", 20, "02:00", "Bram Ostenholt", "Nerys Quillon-Marsh",
        "normal", "Moves statements older than 18 months to the cheaper storage tier. Done in one night.")
    add("ITC-8106", "identity-service", "Rotate the token signing key of the identity service", 9, "14:02", "Marit Doveleigh",
        "Nerys Quillon-Marsh", "standard",
        "Replaces the key that signs session tokens. Services fetch the new public key from the identity service and cache it. "
        "The plan said 22:00 that evening. The team did it at 14:02, ahead of plan. The record was corrected to 14:02 at 16:40 the same day.",
        scheduled=stamp(today, 9, "22:00"), note="Time corrected after the incident INC-7004. It was first recorded as 22:00.")
    return ch


def build_runbooks() -> dict:
    def rb(service, owner, steps):
        return {"service": service, "owner": owner, "note": "Every step marked as needing approval is for a person to run. This service cannot run a step.",
                "steps": [{"step": i, "action": a, "who_may_run_it": w} for i, (a, w) in enumerate(steps, start=1)]}

    return {
        "payment-service": rb("payment-service", "Payments engineering", [
            ("Check the error rate, p95 latency and volume on dashboard DASH-1001. Note the time the numbers left their normal range.", "any on-call engineer"),
            ("Look at the change list for the service for the last 24 hours. A release or flag change near the start time is the first suspect.", "any on-call engineer"),
            ("Check the CPU of the payments database. Above 80 percent for 10 minutes means the service is waiting on the database.", "any on-call engineer"),
            ("If a feature flag was switched on in the last hour, switch it off with the flag console. This needs the approval of the incident manager.", "incident manager approves, on-call engineer runs"),
            ("If no flag explains it, roll back to the previous release with the deploy pipeline. This needs the approval of the change manager.", "change manager approves, release engineer runs"),
            ("After any step, watch the three measures for 15 minutes before declaring recovery. Tell the contact centre when payments are normal.", "incident manager")]),
        "card-authorisation": rb("card-authorisation", "Cards engineering", [
            ("Check the error rate and volume on dashboard DASH-1002. A step change to near 100 percent that began at a clean minute points to an expiry or a switched-off dependency.", "any on-call engineer"),
            ("Read the last 50 error lines of the authorisation log. Look for TLS, certificate, timeout or connection words.", "any on-call engineer"),
            ("Open the certificate dashboard DASH-1003. Check the expiry time of every certificate used by the service.", "any on-call engineer"),
            ("If a certificate has expired, raise an urgent renewal request with the certificate team and tell the card processor's help desk.", "any on-call engineer"),
            ("Install the renewed certificate only through a change record. It needs the approval of the change manager.", "change manager approves, platform engineer runs"),
            ("Check the change list for the service. A recent change is a second suspect. State in the incident whether there was one.", "any on-call engineer")]),
        "statement-service": rb("statement-service", "Customer channels engineering", [
            ("When an alert says no data, first look at measures the service writes itself, such as the application log volume and the error rate.", "any on-call engineer"),
            ("If those are normal, the fault is in monitoring and not in the service. Find the collector host named in the alert.", "any on-call engineer"),
            ("Check whether the collector process is running and when it last sent data.", "any on-call engineer"),
            ("Restart the collector only through the monitoring team. Do not restart the statement service.", "monitoring team"),
            ("Record the gap (start and end time) in the incident so that reports of volume for that period are read with care.", "any on-call engineer")]),
        "online-banking": rb("online-banking", "Customer channels engineering", [
            ("Check the login error rate and latency on the online banking dashboard.", "any on-call engineer"),
            ("Read the error text in the login log. Group by message, not by count.", "any on-call engineer"),
            ("Check the database connection pool. Above 90 percent in use means the pool is the likely problem.", "any on-call engineer"),
            ("Check the change list for online-banking and the identity service for the last 24 hours.", "any on-call engineer"),
            ("Flush the key cache on the application nodes if the log says the token signature is invalid. This needs the approval of the incident manager.", "incident manager approves, on-call engineer runs")]),
        "notification-service": rb("notification-service", "Customer channels engineering", [
            ("Check the queue depth and the age of the oldest message.", "any on-call engineer"),
            ("Check the change list for the last 24 hours.", "any on-call engineer"),
            ("Check the text-message provider's status page for known delays.", "any on-call engineer"),
            ("Scale the workers up only through a change record.", "change manager approves, platform engineer runs")]),
        "ledger-posting": rb("ledger-posting", "Core engineering", [
            ("Check the posting error rate and the count of postings waiting.", "any on-call engineer"),
            ("Check for a lock held by a long batch on the ledger tables.", "any on-call engineer"),
            ("Stopping or restarting a batch needs the approval of the incident manager.", "incident manager approves, core engineer runs")]),
        "reporting-database": rb("reporting-database", "Data platform", [
            ("Check disk use and the age of the newest log file.", "any on-call engineer"),
            ("Check whether a nightly job is still running.", "any on-call engineer"),
            ("Freeing space (archive or purge) needs the approval of the data owner.", "data owner approves, data engineer runs")]),
        "mobile-gateway": rb("mobile-gateway", "Customer channels engineering", [
            ("Check the error rate by app version.", "any on-call engineer"),
            ("Check the change list for the gateway and the identity service.", "any on-call engineer"),
            ("A rollback needs the approval of the change manager.", "change manager approves, release engineer runs")]),
    }


def build_dashboards() -> dict:
    def m(title, service, measure, warn, crit, higher_is_bad=True):
        return {"kind": "measure", "title": title, "service": service, "measure": measure, "warn": warn, "crit": crit,
                "higher_is_bad": higher_is_bad}

    return {
        "DASH-1001": {"dashboard_id": "DASH-1001", "title": "Payments health", "panels": [
            m("Payment service p95 latency", "payment-service", "latency_p95_ms", 1000, 2000),
            m("Payment service error rate", "payment-service", "error_rate_pct", 1, 3),
            m("Payment service volume", "payment-service", "volume_per_min", 0, 0),
            m("Payments database CPU", "payment-service", "payments_db_cpu_pct", 70, 90)]},
        "DASH-1002": {"dashboard_id": "DASH-1002", "title": "Card authorisation health", "panels": [
            m("Authorisation error rate", "card-authorisation", "error_rate_pct", 2, 5),
            m("Authorisation p95 latency", "card-authorisation", "latency_p95_ms", 400, 800),
            m("Authorisation volume", "card-authorisation", "volume_per_min", 0, 0)]},
        "DASH-1003": {"dashboard_id": "DASH-1003", "title": "Certificate expiry", "panels": [
            {"kind": "certificates", "title": "Certificates used by the bank's services"}]},
        "DASH-1004": {"dashboard_id": "DASH-1004", "title": "Statement service", "panels": [
            m("Volume (monitoring collector)", "statement-service", "volume_per_min", 0, 0),
            m("Volume (application log)", "statement-service", "volume_from_app_log_per_min", 0, 0),
            m("Error rate", "statement-service", "error_rate_pct", 1, 3),
            m("p95 latency", "statement-service", "latency_p95_ms", 1000, 2000)]},
    }


def build_certificates(today: date) -> list[dict]:
    rows = [("cardproc-mtls-client", "card-authorisation", stamp(today, 0, "04:58"), "Client certificate for the link to the card processor."),
            ("payments-hub-tls", "payment-service", stamp(today, -212, "09:00"), "Server certificate of the payments hub."),
            ("online-banking-tls", "online-banking", stamp(today, -143, "09:00"), "Server certificate of online banking."),
            ("mobile-gateway-tls", "mobile-gateway", stamp(today, -58, "09:00"), "Server certificate of the mobile gateway."),
            ("statement-service-tls", "statement-service", stamp(today, -301, "09:00"), "Server certificate of the statement service.")]
    return [{"certificate": c, "service": s, "expires_at": e, "purpose": p} for c, s, e, p in rows]


def tl(today, ago, hhmm, who, entry):
    return {"time": stamp(today, ago, hhmm), "who": who, "entry": entry}


def build_incidents(today: date) -> dict:
    inc = {}
    inc["INC-7001"] = {
        "incident_id": "INC-7001", "title": "Payments are slow", "status": "open", "severity": "high",
        "opened_at": stamp(today, 0, "08:46"), "resolved_at": "", "closed_at": "",
        "reported": "The monitoring alert ALT-9101 reported that the 95th percentile response time of payment-service was above 2000 ms for 5 minutes. "
                    "The contact centre began to report slow payment screens at 08:55.",
        "alert_id": "ALT-9101", "alert_text": "payment-service p95 latency above 2000 ms for 5 minutes",
        "services_affected": ["payment-service", "online-banking"], "linked_change_ids": ["ITC-8101", "ITC-8102"],
        "timeline": [tl(today, 0, "08:00", "deployment pipeline", "Release 4.18.0 of payment-service deployed to all four nodes (ITC-8101)."),
                     tl(today, 0, "08:15", "release schedule", "Flag duplicate_check_enabled switched on, as planned in ITC-8101."),
                     tl(today, 0, "08:46", "monitoring", "Alert ALT-9101 fired. Incident opened."),
                     tl(today, 0, "08:49", ON_CALL["payments"], "Acknowledged the alert. Looking at dashboard DASH-1001."),
                     tl(today, 0, "08:55", "contact centre", "14 calls so far from customers whose payment screen is slow or times out."),
                     tl(today, 0, "09:10", ON_CALL["payments"], "CPU of the payments database is at 91 percent. It was about 35 percent before 08:20."),
                     tl(today, 0, "09:20", ON_CALL["manager"], "Took over as incident manager. No action has been taken on the service yet.")],
        "assessments": [], "reviews": []}
    inc["INC-7002"] = {
        "incident_id": "INC-7002", "title": "Card purchases are being declined", "status": "open", "severity": "critical",
        "opened_at": stamp(today, 0, "05:08"), "resolved_at": "", "closed_at": "",
        "reported": "The monitoring alert ALT-9102 reported that more than 5 percent of card authorisations ended in a technical error for 5 minutes.",
        "alert_id": "ALT-9102", "alert_text": "card-authorisation error rate above 5 percent for 5 minutes",
        "services_affected": ["card-authorisation"], "linked_change_ids": [],
        "timeline": [tl(today, 0, "05:08", "monitoring", "Alert ALT-9102 fired. Incident opened."),
                     tl(today, 0, "05:12", ON_CALL["cards"], "Acknowledged the alert."),
                     tl(today, 0, "05:25", ON_CALL["cards"], "The authorisation log shows repeated lines: TLS handshake failed, certificate has expired (peer: card processor, "
                                                           "client certificate cardproc-mtls-client)."),
                     tl(today, 0, "05:40", ON_CALL["cards"], "Checked the change calendar and the change list for card-authorisation. The last change was 12 days ago (ITC-8104). "
                                                           "Nothing is planned for today."),
                     tl(today, 0, "06:05", ON_CALL["cards"], "The certificate dashboard DASH-1003 shows cardproc-mtls-client expired at 04:58 today."),
                     tl(today, 0, "06:30", ON_CALL["cards"], "Urgent renewal requested from the certificate team. The renewed certificate is not yet issued.")],
        "assessments": [], "reviews": []}
    inc["INC-7003"] = {
        "incident_id": "INC-7003", "title": "No volume data from the statement service", "status": "open", "severity": "medium",
        "opened_at": stamp(today, 0, "09:36"), "resolved_at": "", "closed_at": "",
        "reported": "The monitoring alert ALT-9103 reported that no volume data had arrived for the statement service for 36 minutes, since 09:00.",
        "alert_id": "ALT-9103", "alert_text": "statement-service volume_per_min: no data for 36 minutes (last sample 09:00)",
        "services_affected": ["statement-service"], "linked_change_ids": [],
        "timeline": [tl(today, 0, "09:36", "monitoring", "Alert ALT-9103 fired. Incident opened."),
                     tl(today, 0, "09:40", ON_CALL["platform"], "Acknowledged. The alert names the collector on host stmt-app-02."),
                     tl(today, 0, "09:44", "monitoring", "The collector on stmt-app-02 restarted under its watchdog."),
                     tl(today, 0, "09:50", "monitoring", "Volume samples are arriving again.")],
        "assessments": [], "reviews": []}
    inc["INC-7004"] = {
        "incident_id": "INC-7004", "title": "Customers cannot log in to online banking", "status": "closed", "severity": "high",
        "opened_at": stamp(today, 9, "14:08"), "resolved_at": stamp(today, 9, "15:32"), "closed_at": stamp(today, 8, "10:00"),
        "reported": "The monitoring alert ALT-9104 reported that more than 10 percent of login requests to online banking failed for 5 minutes.",
        "alert_id": "ALT-9104", "alert_text": "online-banking login error rate above 10 percent for 5 minutes",
        "services_affected": ["online-banking", "mobile-gateway"], "linked_change_ids": ["ITC-8106"],
        "resolution_note": "The key cache was flushed on both application nodes at 15:25. Logins recovered by 15:32.",
        "timeline": [tl(today, 9, "14:02", "identity team", "Signing key of the identity service rotated (ITC-8106). The change record said 22:00."),
                     tl(today, 9, "14:08", "monitoring", "Alert ALT-9104 fired. Incident opened."),
                     tl(today, 9, "14:12", ON_CALL["platform"], "Acknowledged the alert."),
                     tl(today, 9, "14:20", ON_CALL["platform"], "Login latency is up from 320 ms to 1,100 ms. Suspected cause: database connection pool exhaustion."),
                     tl(today, 9, "14:35", ON_CALL["platform"], "Connection pool restarted on both application nodes. Error rate unchanged."),
                     tl(today, 9, "14:50", "database team", "Database is healthy and the pool is at 41 percent use. The pool is not the cause."),
                     tl(today, 9, "15:05", ON_CALL["platform"], "A customer's screenshot says: session token not accepted. The login log says: token signature invalid."),
                     tl(today, 9, "15:12", "identity team", "They rotated the signing key at 14:02, ahead of the 22:00 plan. Online banking caches the old public key for up to 24 hours."),
                     tl(today, 9, "15:25", ON_CALL["platform"], "Key cache flushed on both application nodes."),
                     tl(today, 9, "15:32", "monitoring", "Login error rate is below 2 percent. Incident resolved."),
                     tl(today, 9, "16:40", ON_CALL["manager"], "Change record ITC-8106 corrected to show the real time, 14:02."),
                     tl(today, 8, "10:00", ON_CALL["manager"], "Incident closed. A post-incident review is due.")],
        "assessments": [], "reviews": []}
    return inc


def build_itops(today: date) -> dict:
    return {"itops_incidents": build_incidents(today), "itops_metrics": build_metrics(today), "itops_changes": build_changes(today),
            "itops_runbooks": build_runbooks(), "itops_dashboards": build_dashboards(), "itops_certificates": build_certificates(today)}


# ------------------------------------------------------------------ simulated incidents (rotating templates)

def sim_incident(data: dict, today: date, kind: int, num: int) -> tuple[str, str]:
    iid = f"INC-{7100 + num}"
    t = times("08:00", 10, 13)
    specs = [
        ("notification-service", "Payment receipts are delayed", "medium", "ALT-9201", "notification-service queue depth above 500 for 10 minutes",
         "The queue of messages waiting to be sent grew from about 12 to more than 900 in 30 minutes. Text-message delivery is late.",
         {"queue_depth": [12, 13, 11, 12, 12, 13, 14, 60, 240, 520, 780, 910, 960], "error_rate_pct": baseline(13, 0.2, [0.0, 0.1]),
          "latency_p95_ms": [140, 144, 137, 142, 135, 144, 141, 180, 420, 760, 910, 980, 1010], "volume_per_min": [85, 87, 83, 86, 84, 87, 85, 70, 48, 30, 22, 18, 17]},
         "Customers get receipts late. No money is affected."),
        ("reporting-database", "Disk almost full on the reporting database", "high", "ALT-9202", "reporting-database disk used above 90 percent",
         "Disk use rose from 61 percent to 93 percent in two hours. A nightly job did not finish and kept its temporary files.",
         {"disk_used_pct": [61, 63, 66, 69, 72, 76, 80, 84, 87, 89, 91, 92, 93], "error_rate_pct": baseline(13, 0.2, [0.0, 0.1]),
          "latency_p95_ms": baseline(13, 520, [0, 6, -4]), "volume_per_min": baseline(13, 14, [0, 1, -1])},
         "Reports may fail when the disk fills. Payments are not affected."),
        ("ledger-posting", "Alert storm from one rule, service looks normal", "low", "ALT-9203", "ledger-posting error rate above 5 percent (rule LR-12)",
         "Rule LR-12 fired 40 times in 10 minutes. It reads a counter that was reset by a monitoring upgrade. The service's own measures are normal.",
         {"error_rate_pct": baseline(13, 0.2, [0.0, 0.1, -0.1]), "latency_p95_ms": baseline(13, 310, [0, 4, -3]),
          "volume_per_min": baseline(13, 60, [0, 2, -2])},
         "None known."),
        ("mobile-gateway", "Mobile app logins fail for one app version", "high", "ALT-9204", "mobile-gateway error rate above 8 percent for 5 minutes",
         "Login failures rose from 0.2 percent to 11 percent at 08:40. A release of the mobile app went to customers at 08:30.",
         {"error_rate_pct": [0.2, 0.2, 0.3, 0.2, 0.2, 0.3, 0.2, 0.3, 11.2, 11.6, 11.4, 11.8, 11.5], "latency_p95_ms": baseline(13, 210, [0, 4, -3]),
          "volume_per_min": [480, 482, 478, 481, 479, 483, 480, 482, 470, 455, 452, 449, 451]},
         "Customers on the new app version cannot log in."),
    ]
    svc, title, sev, alert, alert_text, reported, series, impact = specs[kind % 4]
    for measure, vals in series.items():
        data["itops_metrics"].setdefault(svc, {})[measure] = points(today, 0, t, vals)
    data["itops_incidents"][iid] = {
        "incident_id": iid, "title": title, "status": "open", "severity": sev, "opened_at": stamp(today, 0, "09:50"), "resolved_at": "",
        "closed_at": "", "reported": reported, "alert_id": alert, "alert_text": alert_text, "services_affected": [svc], "linked_change_ids": [],
        "timeline": [tl(today, 0, "09:50", "monitoring", f"Alert {alert} fired. Incident opened."), tl(today, 0, "09:52", ON_CALL["platform"], "Acknowledged the alert.")],
        "assessments": [], "reviews": [], "customer_impact_note": impact}
    msg = (f"A new incident {iid} has been opened in the itops system for {svc}: {title.lower()}. Its severity is {sev}. "
           f"Read it with get_incident, then read the metrics and the runbook before you assess it.")
    return iid, msg
