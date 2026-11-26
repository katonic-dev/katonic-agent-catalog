"""The regulator test feeds: two invented RSS feeds with a fresh state per series, for testing a monitoring workflow."""
import html
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime

import pytest

from conftest import H, TODAY

FEEDS = ("fca", "ecb")


def feed(client, path, status=200):
    r = client.get(path)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r


def post(client, path, status=200):
    r = client.post(path, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def tidy(x: str) -> str:
    """The body of the code steps n_tidy_a and n_tidy_b in
    banking/agents/regulatory-monitoring/workflow.yaml, copied as it stands there (prints collected instead)."""
    out = []

    def tag(s, t):
        m = re.search(r'<' + t + r'[^>]*>(.*?)</' + t + '>', s, re.S)
        if not m:
            return ''
        v = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', m.group(1), flags=re.S)
        return ' '.join(html.unescape(v).split())
    items = re.findall(r'<item\b[^>]*>(.*?)</item>', x, re.S)
    for it in items:
        out.append(' | '.join([tag(it, 'pubDate'), tag(it, 'title'), tag(it, 'link')]))
    if not items:
        out.append('UNREADABLE')
    return "\n".join(out)


@pytest.mark.parametrize("name", FEEDS)
def test_starting_items_are_invented_rss_and_need_no_key(client, name):
    r = feed(client, f"/feeds/{name}.xml")
    assert "rss+xml" in r.headers["content-type"] and r.headers["x-demo-data"] == "invented"
    root = ET.fromstring(r.content)
    channel = root.find("channel")
    assert root.tag == "rss" and root.attrib["version"] == "2.0"
    assert channel.find("title").text.startswith("Test copy") and "invented" in channel.find("description").text
    items = root.findall("./channel/item")
    assert len(items) == 8
    dates = [datetime.strptime(it.find("pubDate").text.replace("GMT", "+0000"), "%a, %d %b %Y %H:%M:%S %z").date()
             for it in items]
    assert dates == sorted(dates, reverse=True) and dates[0] == date.fromisoformat(TODAY)
    assert all(it.find("link").text.startswith(f"https://feeds.meridian-demo.example/{name}/") for it in items)
    assert all(it.find("title").text.startswith("Test ") for it in items)
    assert r.text == feed(client, f"/feeds/default/{name}.xml").text == feed(client, f"/feeds/fresh-1/{name}.xml").text


def test_layouts_follow_the_two_live_feeds(client):
    fca, ecb = feed(client, "/feeds/fca.xml").text, feed(client, "/feeds/ecb.xml").text
    assert all(line.count("<") <= 2 for line in fca.splitlines())  # one element per line
    assert len(ecb.splitlines()) == 4 and ecb.splitlines()[2].count("<item>") == 8  # every item on one long line


def test_two_series_are_independent(client):
    post(client, "/admin/feeds/run-a/fca/publish")
    post(client, "/admin/feeds/run-b/ecb/unreadable?on=true")
    a, b = admin_view(client, "run-a"), admin_view(client, "run-b")
    assert a["fca"]["count"] == 9 and a["ecb"]["count"] == 8 and not a["ecb"]["unreadable"]
    assert b["fca"]["count"] == 8 and b["ecb"]["unreadable"]
    assert feed(client, "/feeds/run-b/fca.xml").text == feed(client, "/feeds/fca.xml").text
    feed(client, "/feeds/run-a/ecb.xml")
    feed(client, "/feeds/run-b/ecb.xml", status=503)


def admin_view(client, series):
    r = client.get(f"/admin/feeds/{series}", headers=H)
    assert r.status_code == 200
    return r.json()["feeds"]


@pytest.mark.parametrize("name", FEEDS)
def test_publish_adds_one_item_at_the_top_and_leaves_the_rest_byte_for_byte(client, name):
    before = feed(client, f"/feeds/t3/{name}.xml").text
    added = post(client, f"/admin/feeds/t3/{name}/publish")
    after = feed(client, f"/feeds/t3/{name}.xml").text
    cut = before.index("<item>")
    assert after[:cut] == before[:cut]
    new = after[cut:len(after) - len(before) + cut]
    assert after.endswith(before[cut:]) and new.count("<item>") == 1 and new.rstrip().endswith("</item>")
    assert added["count"] == 9 and set(added["item"]) == {"title", "date", "link"}
    assert added["item"]["title"] in new and added["item"]["link"] in new
    assert added["item"]["date"] == "2026-11-25"
    second = post(client, f"/admin/feeds/t3/{name}/publish")["item"]
    assert second["date"] == "2026-11-26" and second["title"] != added["item"]["title"]
    titles = [it["title"] for it in admin_view(client, "t3")[name]["items"]]
    assert titles[:2] == [second["title"], added["item"]["title"]] and len(titles) == 10


def test_publish_titles_are_the_same_in_every_series(client):
    one = post(client, "/admin/feeds/x1/ecb/publish")["item"]
    two = post(client, "/admin/feeds/x2/ecb/publish")["item"]
    assert one == two


@pytest.mark.parametrize("name", FEEDS)
def test_unreadable_gives_503_and_off_restores_the_same_document(client, name):
    before = feed(client, f"/feeds/t4/{name}.xml").text
    assert post(client, f"/admin/feeds/t4/{name}/unreadable?on=true")["unreadable"] is True
    r = feed(client, f"/feeds/t4/{name}.xml", status=503)
    assert r.headers["content-type"].startswith("text/plain") and "unreadable" in r.text
    assert tidy(r.text) == "UNREADABLE"
    assert post(client, f"/admin/feeds/t4/{name}/unreadable?on=false")["unreadable"] is False
    assert feed(client, f"/feeds/t4/{name}.xml").text == before


def test_reset_of_feeds_puts_every_series_back_and_leaves_the_rest(client, store):
    start = {name: feed(client, f"/feeds/{name}.xml").text for name in FEEDS}
    post(client, "/admin/feeds/default/fca/publish")
    post(client, "/admin/feeds/r1/ecb/unreadable?on=true")
    assert client.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H).status_code == 200
    state = client.get("/admin/state", headers=H).json()
    assert state["changed_by"]["feeds"] == ["feed_series"]
    r = post(client, "/admin/reset/feeds")
    assert r["put_back"] == ["feed_series"] and store.data["feed_series"] == {}
    assert feed(client, "/feeds/fca.xml").text == start["fca"] and feed(client, "/feeds/r1/ecb.xml").text == start["ecb"]
    assert client.get("/cards/cards/CRD-2001", headers=H).json()["status"] == "blocked"
    post(client, "/admin/feeds/r1/fca/publish")
    post(client, "/admin/reset")
    assert feed(client, "/feeds/r1/fca.xml").text == start["fca"]


def test_reads_store_nothing_and_admin_routes_need_the_key(client, store):
    feed(client, "/feeds/never-changed/fca.xml")
    admin_view(client, "never-changed")
    assert store.data["feed_series"] == {}
    assert client.post("/admin/feeds/a/fca/publish").status_code == 401
    assert client.get("/admin/feeds/a").status_code == 401
    feed(client, "/feeds/Not_Valid/fca.xml", status=404)
    feed(client, "/feeds/a/boe.xml", status=404)
    assert client.post("/admin/feeds/a/boe/publish", headers=H).status_code == 404
    assert not any(p.startswith(("/feeds", "/admin")) for s in ("news", "core")
                   for p in client.get(f"/{s}/openapi.json").json()["paths"])


@pytest.mark.parametrize("name", FEEDS)
def test_the_workflow_tidy_step_gives_one_line_per_item(client, name):
    post(client, f"/admin/feeds/t6/{name}/publish")
    text = feed(client, f"/feeds/t6/{name}.xml").text
    assert "'''" not in text and not text.endswith("\\")  # the step pastes the body into r'''...'''
    lines = tidy(text).splitlines()
    items = admin_view(client, "t6")[name]["items"]
    assert len(lines) == len(items) == 9
    for line, it in zip(lines, items):
        when, title, link = line.split(" | ")
        assert title == it["title"] and link == it["link"]
        assert datetime.strptime(when.replace("GMT", "+0000"), "%a, %d %b %Y %H:%M:%S %z").date().isoformat() == it["date"]
    assert any("&" in line for line in lines) or name == "ecb"  # an escaped ampersand comes out plain
