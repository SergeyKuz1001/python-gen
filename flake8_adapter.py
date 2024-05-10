from framework.adapters import SubprocessAdapter


class Flake8Adapter:
    class Usual(SubprocessAdapter):
        @property
        def identifier(self) -> str:
            return "flake8"

        @property
        def shell_script(self) -> str:
            return "flake8 {} | cut -f2 -d' ' | sort | uniq"

        @property
        def error_message(self) -> str:
            return "Error from flake8 for file {}"
