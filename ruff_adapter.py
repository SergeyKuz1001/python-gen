from framework.adapters import SubprocessAdapter


class RuffAdapter:
    class Usual(SubprocessAdapter):
        @property
        def identifier(self) -> str:
            return "ruff"

        @property
        def shell_script(self) -> str:
            return "ruff check --statistics {} | cut -f2"

        @property
        def error_message(self) -> str:
            return "Error from ruff for file {}"
