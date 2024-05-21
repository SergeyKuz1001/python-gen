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
                ("+uv-sa",),
                ("+uv",),
                ("-uv",),
                ("+un",),
                ("-un",),
                ("+it",),
                ("+it-pr",),
                ("-it",),
                ("-it-ch",),
                ("-it-ld",),
                ("+il",),
                ("-il",),
                ("-il-ch",),
                ("+uv-sa", "+uv"),
                ("+it", "+it-pr"),
                ("-it", "-it-ch"),
                ("-it", "-it-ld"),
                ("-it-ch", "-it-ld"),
                ("-il", "-il-ch"),
                ("-uv", "-un"),
                ("+uv-sa", "-un"),
                ("+it", "+il"),
                ("-it-ch", "+un"),
                ("-uv", "-un", "-it"),
                ("-uv", "-un", "+it"),
                ("+il", "-uv", "-un"),
                ("-uv", "-un", "-il-ch"),
                ("-uv", "-un", "-il-ch", "-it-ch"),
                ("+uv-sa", "+un", "+it-pr", "+il"),
            ]:
                success = Tester(
                    SimpleGenerator.FromArgs(seed, args), adapter, "codes"
                ).test_linter()
                if not success:
                    print(
                        f"Error for seed = {seed}, args = {args}, adapter = {adapter.identifier}"
                    )
        new_percentage = 100 * (seed + 1) // N
        if new_percentage > percentage:
            percentage = new_percentage
            print(f"{percentage}%")
