from simple_generator import SimpleGenerator
from ruff_adapter import RuffAdapter
from flake8_adapter import Flake8Adapter
from framework import Tester


if __name__ == "__main__":
    N = 100
    percentage = 0
    for seed in range(N):
        for adapter in (RuffAdapter.Usual(), Flake8Adapter.Usual()):
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
                Tester(SimpleGenerator.FromArgs(seed, args), adapter, "codes").test_linter()
        new_percentage = 100 * (seed + 1) // N
        if new_percentage > percentage:
            percentage = new_percentage
            print(f"{percentage}%")
