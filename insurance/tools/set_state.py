"""Record that an insurance agent is built on a cluster and passes its tests.

Usage, from anywhere inside the repository:

    python insurance/tools/set_state.py <agent-folder> <note-file> <readme-state-text> <index-old-tail> <index-new-tail>

It rewrites three places so that they agree:

1. the `state` block of insurance/agents/<agent-folder>/agent.yaml (whatever the old note was, one line or folded),
2. the State row of that folder's README.md,
3. the end of the agent's row in insurance/README.md (<index-old-tail> is replaced by <index-new-tail>).

It stops without writing a file it cannot match: each target must be found exactly once.
See insurance/BUILD-ON-A-CLUSTER.md, step 4.
"""
import io
import os
import sys

if len(sys.argv) != 6:
    sys.exit(__doc__)

A = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")) + os.sep
agent, note_file, readme_state, idx_old, idx_new = sys.argv[1:6]
note = " ".join(io.open(note_file, encoding="utf-8").read().split())
assert note, "the note file is empty"


def read(path):
    s = io.open(path, encoding="utf-8", newline="").read()
    return s, ("\r\n" if "\r\n" in s else "\n")


def write(path, lines, nl):
    io.open(path, "w", encoding="utf-8", newline="").write(nl.join(lines))


# Work everything out first, write last, so that a failed match leaves all three files as they were.

# agent.yaml: from "state:" to the end of its block
p1 = os.path.join(A, "agents", agent, "agent.yaml")
s, nl1 = read(p1)
l1 = s.split(nl1)
i = [k for k, l in enumerate(l1) if l.startswith("state:")]
assert len(i) == 1, "agent.yaml: expected one 'state:' line, found %d" % len(i)
i = i[0]
j = i + 1
while j < len(l1) and (l1[j].startswith(" ") or l1[j] == ""):
    j += 1
while l1[j - 1] == "":
    j -= 1
shelf = [l for l in l1[i:j] if l.strip().startswith("on_the_catalog_shelf:")]
assert len(shelf) == 1, "agent.yaml: expected one 'on_the_catalog_shelf:' line in the state block"
l1[i:j] = ["state:", "  built_on_a_cluster: true", "  tests_passed: true", shelf[0], "  notes: >", "    " + note]

# README State row
p2 = os.path.join(A, "agents", agent, "README.md")
s, nl2 = read(p2)
l2 = s.split(nl2)
h = [k for k, l in enumerate(l2) if l.startswith("| State |")]
assert len(h) == 1, "README.md: expected one '| State |' row, found %d" % len(h)
l2[h[0]] = "| State | " + readme_state + " |"

# index row
p3 = os.path.join(A, "README.md")
s, nl3 = read(p3)
l3 = s.split(nl3)
h = [k for k, l in enumerate(l3) if "(agents/%s/README.md)" % agent in l]
assert len(h) == 1, "index: expected one row for %s, found %d" % (agent, len(h))
assert l3[h[0]].count(idx_old) == 1, "index: the old tail is not in the row exactly once: ..." + l3[h[0]][-200:]
l3[h[0]] = l3[h[0]].replace(idx_old, idx_new)

write(p1, l1, nl1)
write(p2, l2, nl2)
write(p3, l3, nl3)
print("state set for", agent)
