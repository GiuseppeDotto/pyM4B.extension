from typing import Tuple, Set, Iterable, List


class JournalingAttribute:
    def __init__(self, mode: JournalingMode): ...
    @property
    def Mode(self) -> JournalingMode: ...


class RegenerationAttribute:
    def __init__(self, option: RegenerationOption): ...
    @property
    def Option(self) -> RegenerationOption: ...


class TransactionAttribute:
    def __init__(self, mode: TransactionMode): ...
    @property
    def Mode(self) -> TransactionMode: ...


class JournalingMode:
    UsingCommandData = 0
    NoCommandData = 1


class RegenerationOption:
    Manual = 0


class TransactionMode:
    Manual = 1
    ReadOnly = 2
