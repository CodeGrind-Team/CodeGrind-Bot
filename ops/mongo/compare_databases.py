"""
Compare the `bot` database on two MongoDB clusters to confirm a migration copied
everything. Read-only on both sides.

Checks per collection: document count, index definitions, and a checksum over
every document (sorted by _id), so any missing or altered document is caught.

Usage: see "Migrating from Atlas" in ops/README.md. The URIs are read from the
SRC_URI and DST_URI environment variables so they don't land in shell history.
"""

import hashlib
import os
import sys

from bson import BSON
from pymongo import MongoClient

DB_NAME = "bot"


def collection_report(db):
    report = {}
    for name in sorted(db.list_collection_names()):
        if name.startswith("system."):
            continue
        coll = db[name]
        digest = hashlib.sha256()
        count = 0
        for doc in coll.find({}, sort=[("_id", 1)]):
            digest.update(BSON.encode(doc))
            count += 1
        indexes = sorted(
            (ix["name"], tuple(ix["key"].items()), bool(ix.get("unique", False)))
            for ix in coll.list_indexes()
        )
        report[name] = {"count": count, "sha256": digest.hexdigest(), "indexes": indexes}
    return report


def main():
    src = MongoClient(os.environ["SRC_URI"])[DB_NAME]
    dst = MongoClient(os.environ["DST_URI"])[DB_NAME]

    print("Reading source...")
    a = collection_report(src)
    print("Reading destination...")
    b = collection_report(dst)

    ok = True
    for name in sorted(set(a) | set(b)):
        sa, sb = a.get(name), b.get(name)
        if sa is None or sb is None:
            print(f"[FAIL] {name}: missing on {'source' if sa is None else 'destination'}")
            ok = False
            continue
        problems = [k for k in ("count", "sha256", "indexes") if sa[k] != sb[k]]
        status = "OK  " if not problems else "FAIL"
        print(f"[{status}] {name}: src={sa['count']} dst={sb['count']} docs"
              + (f"  mismatched: {', '.join(problems)}" if problems else ""))
        ok &= not problems

    print("\nALL MATCH - safe to switch over." if ok else "\nMISMATCH - do NOT switch over.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
