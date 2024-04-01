import generate
from rule_checker import RuleChecker

import subprocess


def main():
    for seed in range(100):
        for args in [
            (),
            ("-uv",),
            ("-un",),
            ("-uv", "-un"),
            ("-it",),
            ("+it",),
            ("-it", "-uv", "-un"),
            ("+it", "-uv", "-un"),
            ("-uv", "-un", "-it"),
            ("-uv", "-un", "+it"),
        ]:
            filename = f"codes/code_{seed}_{'_'.join(args)}.txt"
            code, generator = generate.main(seed, args)
            with open(filename, "w") as fout:
                print(code, file=fout)
            proc = subprocess.run(
                f"ruff check --statistics {filename} | cut -f2",
                shell=True,
                stdout=subprocess.PIPE,
            )
            if proc.returncode != 0:
                print(f"Error from ruff for seed = {seed}, args = {' '.join(args)}")
                continue
            rules = proc.stdout.decode("utf-8").splitlines()
            for rule_checker in filter(
                lambda checker: isinstance(checker, RuleChecker), generator.checkers
            ):
                if not rule_checker.in_rules(rules, generator):
                    print(
                        f"Error from checker for seed = {seed}, args = {' '.join(args)}"
                    )


if __name__ == "__main__":
    main()
