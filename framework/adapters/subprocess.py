from .abstract import AbstractAdapter

from ..failures import UnexpectedFailure

from abc import ABC, abstractmethod
import subprocess


class SubprocessAdapter(AbstractAdapter, ABC):
    @property
    @abstractmethod
    def shell_script(self) -> str: ...

    @property
    def error_message(self) -> str:
        return "Error for file {}"

    def get_rules(self, filename: str) -> list[str]:
        proc = subprocess.run(
            self.shell_script.format(filename),
            shell=True,
            stdout=subprocess.PIPE,
        )
        if proc.returncode != 0:
            raise UnexpectedFailure(self.error_message.format(filename))
        return proc.stdout.decode("utf-8").splitlines()
