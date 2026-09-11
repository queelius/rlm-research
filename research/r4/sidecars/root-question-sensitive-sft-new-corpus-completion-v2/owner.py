"""Run the qualified completion owner against the corrected v2 namespace."""
import recovery as r

owner = r.s.load("new_corpus_completion_v2_owner", r.V1 / "owner.py",
    "6a0affd303c677acea8e8b3b5506a146715cf8bc994e4bce328b1d41f4def3e3",
    {"recovery": r})


if __name__ == "__main__":
    args = owner.parse_args()
    if args.command == "verify":
        print(r.verify()["identity"])
    else:
        value = owner.execute(args.output)
        print({"complete": value["complete"], "elapsed_seconds": value["elapsed_seconds"]})
        raise SystemExit(0 if value["complete"] else 1)
