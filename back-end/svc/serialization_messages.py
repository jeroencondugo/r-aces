#  Copyright (c) 2015-2021 Condugo bvba
from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class Message:
    type: str
    msg: str


@dataclass
class MessageType:
    id: int
    warnings: List[Message]
    errors: List[Message]
    debug: List[Message]  # Only internal debug messages, not for user


@dataclass
class SankeyMessageCollections:
    graphs: List[MessageType]
    nodes: List[MessageType]
    links: List[MessageType]


@dataclass
class EnergyInsightMessageCollections:
    reports: List[MessageType]
    datasets: List[MessageType]



