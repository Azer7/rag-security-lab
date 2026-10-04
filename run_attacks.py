"""Runs every attack and benign question under each defense mode; saves results.csv."""
import csv, json
from rag_app import build_index, answer, DEFENSES, make_llm, describe_llm

tests = json.load(open("attacks.json"))
index = build_index()
llm = make_llm()
print('Model under test:', describe_llm())
rows, summary = [], {}

for mode in DEFENSES:
    hits, ok = 0, 0
    for a in tests["attacks"]:
        reply = answer(a["question"], index, llm, mode)
        success = any(s.lower() in reply.lower() for s in a["success_if_contains_any"])
        hits += success
        rows.append([mode, a["id"], a["type"], "ATTACK_SUCCEEDED" if success else "blocked", reply.replace("\n", " ")])
    for b in tests["benign"]:
        reply = answer(b["question"], index, llm, mode)
        passed = any(s.lower() in reply.lower() for s in b["expect_any"])
        ok += passed
        rows.append([mode, b["id"], "benign", "ok" if passed else "BROKEN", reply.replace("\n", " ")])
    summary[mode] = (hits, len(tests["attacks"]), ok, len(tests["benign"]))
    print(f"{mode:16} attacks succeeded: {hits}/{len(tests['attacks'])}   benign answered: {ok}/{len(tests['benign'])}")

with open("results.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["defense", "test_id", "type", "result", "answer"])
    w.writerows(rows)
print("Saved results.csv. Read the answers: substring checks can misfire (e.g. a refusal that quotes the attack text).")
