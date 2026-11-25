"""Guest Feedback Analysis, the code steps. Plain Python, standard library only.

The labels are a model's judgement. Everything else is code:
- make_batches(feedback): the distinct comment texts of the period, each given a key (K001, K002, ...), cut into
  batches of BATCH lines "K001 | the comment". A model labels one batch a pass. The same words get one label.
- analyse(feedback, replies, period): reads the model's lines "K001 | theme | harm yes or no", checks every label
  against the fixed list (a label outside the list, a key that is missing or a key given twice differently is
  "Unlabelled", never guessed), counts by theme and by restaurant, picks the quotes behind each theme by reference,
  and lists the harm comments first. The counts must add up to the number of comments read, or the code stops.
It returns the body save_feedback_analysis accepts: period, themes, harm_comments, summary, drafted_by.
"""
import json
import re

THEMES = ["Late delivery", "Wrong or missing item", "Cold food", "App and payment", "Praise", "Other"]
HARM = "Harm or a safety matter"
UNLABELLED = "Unlabelled"
BATCH = 20
QUOTES = 3


def _keys(feedback):
    """Distinct comment texts in a fixed order -> key."""
    texts = sorted({" ".join(str(x["comment"]).split()) for x in feedback["items"]})
    return {t: "K%03d" % (i + 1) for i, t in enumerate(texts)}


def make_batches(feedback):
    if feedback.get("total") is not None and int(feedback["total"]) != len(feedback["items"]):
        raise SystemExit("Only %d of %s comments of the period were read. Nothing was analysed." % (len(feedback["items"]), feedback["total"]))
    lines = ["%s | %s" % (k, t.replace("|", "/")) for t, k in sorted(_keys(feedback).items(), key=lambda kv: kv[1])]
    return ["\n".join(lines[i:i + BATCH]) for i in range(0, len(lines), BATCH)]


def _reply_text(r):
    if isinstance(r, dict):
        for k in ("text", "result", "output", "content"):
            if isinstance(r.get(k), str):
                return r[k]
        return json.dumps(r)
    return str(r)


def read_labels(replies):
    """key -> (theme or Unlabelled, harm True/False). A key seen twice with different labels is Unlabelled."""
    canon = {t.lower(): t for t in THEMES}
    out, clash = {}, set()
    for r in replies:
        for line in _reply_text(r).splitlines():
            m = re.match(r"^\W*(K\d{3})\s*\|\s*([^|]*?)\s*\|\s*(?:harm\s*:?\s*)?(yes|no)\W*$", line.strip(), re.I)
            if not m:
                continue
            key, theme, harm = m.group(1).upper(), canon.get(m.group(2).strip().lower(), UNLABELLED), m.group(3).lower() == "yes"
            if key in out and out[key] != (theme, harm):
                clash.add(key)
            out[key] = (theme, harm)
    for k in clash:
        out[k] = (UNLABELLED, False)
    return out


def analyse(feedback, replies, period=""):
    items = sorted(feedback["items"], key=lambda x: x["reference"])
    keys, labels = _keys(feedback), read_labels(replies)
    by_theme, harm, label_of = {}, [], {}
    for x in items:
        theme, is_harm = labels.get(keys[" ".join(str(x["comment"]).split())], (UNLABELLED, False))
        if is_harm:
            harm.append(x)
            label_of[x["reference"]] = HARM
        else:
            by_theme.setdefault(theme, []).append(x)
            label_of[x["reference"]] = theme
    total = sum(len(v) for v in by_theme.values()) + len(harm)
    if total != len(items) or len(label_of) != len(items):
        raise SystemExit("The counts do not add up: %d comments read, %d counted. Nothing was saved." % (len(items), total))
    themes, parts = [], []
    for name in THEMES + [UNLABELLED]:
        rows = by_theme.get(name, [])
        if name == UNLABELLED and not rows:
            continue
        sites = {}
        for x in rows:
            sites[x["site_id"]] = sites.get(x["site_id"], 0) + 1
        quoted = rows[:QUOTES]
        themes.append({"name": name, "count": len(rows), "counts_by_site": dict(sorted(sites.items(), key=lambda kv: (-kv[1], kv[0]))),
                       "quoted_references": [x["reference"] for x in quoted]})
        top = sorted(sites.items(), key=lambda kv: (-kv[1], kv[0]))[:2]
        parts.append("%s: %d comments%s. Quotes: %s" % (
            name, len(rows), (", most at %s" % " then ".join("%s (%d)" % kv for kv in top)) if top else "",
            "; ".join('%s "%s"' % (x["reference"], x["comment"]) for x in quoted) or "none"))
    harm_part = "%d comments describe harm or a safety matter and go to a person first: %s." % (
        len(harm), "; ".join('%s (%s, %s) "%s"' % (x["reference"], x["site_id"], x["channel"], x["comment"]) for x in harm) or "none")
    summary = "%d comments read for %s. %s The other %d by theme, as a model labelled them and code counted them: %s. The counts add up to %d." % (
        len(items), period or "the period", harm_part, len(items) - len(harm), " | ".join(parts), total)
    body = {"period": period, "themes": themes, "harm_comments": [x["reference"] for x in harm], "summary": summary,
            "drafted_by": "Guest Feedback Analysis (code step)"}
    return body, label_of


if __name__ == "__main__":
    import sys
    fb = json.load(open(sys.argv[1], encoding="utf-8"))
    print(json.dumps(make_batches(fb)[:1], indent=1))
