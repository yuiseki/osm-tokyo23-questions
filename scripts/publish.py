#!/usr/bin/env python3
"""Push the questions and their card to the Hugging Face Hub.

What goes up is one file of questions and the three files that explain it.
What stays in git is everything the questions are made of: the per-question
directories, the templates, the seeds and their attributes. Someone using the
set wants the questions; someone changing it wants the directories, and those
are not a dataset.

The card is data/README.md, kept in git and uploaded as it stands, so what the
Hub shows is a file that can be reviewed and diffed rather than a string
buried in this script.

    python3 scripts/publish.py             # dry run, prints the schema
    python3 scripts/publish.py --push      # uploads
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REPO = "yuiseki/osm-tokyo23-questions"


def path(rel):
    return os.path.join(BASE, rel)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=path("data/questions.jsonl"))
    ap.add_argument("--card", default=path("data/README.md"))
    ap.add_argument("--extra", nargs="*", default=[path("data/LICENSE"),
                                                  path("data/provenance.yaml")])
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true", help="actually upload")
    ap.add_argument("--skip-check", action="store_true",
                    help="do not rebuild the jsonl from the directories first")
    a = ap.parse_args()

    # The jsonl is written from the directories and never edited, so publishing
    # a stale one would put out questions that are not the ones in git.
    if not a.skip_check:
        r = subprocess.run([sys.executable, path("scripts/build_jsonl.py"),
                            "--check", "--out", a.questions])
        if r.returncode != 0:
            raise SystemExit("data/questions.jsonl is out of date. "
                             "Run scripts/build_jsonl.py")

    import datasets

    with open(a.questions, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    # The rows are ragged: a question carries a slot only where its template
    # asked for one. from_list takes its schema from the first row, which has
    # neither place_1 nor target nor checked, and the rest would go missing.
    # So every field is declared and absent ones are explicitly null.
    fields = sorted({k for r in rows for k in r})
    features = datasets.Features({k: datasets.Value("string") for k in fields})
    rows = [{k: r.get(k) for k in fields} for r in rows]
    ds = datasets.Dataset.from_list(rows, features=features)
    print(ds)
    print(f"{len(rows)} questions, "
          f"{os.path.getsize(a.questions)/1e3:.0f} KB of jsonl")
    for p in [a.card] + a.extra:
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")
    print(f"card {os.path.relpath(a.card, BASE)}, plus " +
          ", ".join(os.path.relpath(p, BASE) for p in a.extra))
    if not a.push:
        print("dry run. pass --push to upload")
        return 0

    from huggingface_hub import DatasetCard, HfApi

    api = HfApi()
    # Nothing else creates it. push_to_hub and upload_file both assume the
    # repository is already there and answer 404 when it is not.
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True)

    # Card first, dataset second. push_to_hub writes a dataset_info block into
    # the card's front matter, and pushing the card afterwards would erase it.
    DatasetCard(open(a.card, encoding="utf-8").read()).push_to_hub(
        a.repo, repo_type="dataset")
    for p in a.extra:
        api.upload_file(path_or_fileobj=p, path_in_repo=os.path.basename(p),
                        repo_id=a.repo, repo_type="dataset")
    ds.push_to_hub(a.repo)
    print(f"pushed to {a.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
