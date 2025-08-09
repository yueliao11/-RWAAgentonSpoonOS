# Services module for SpoonAI

from .rwa_data_aggregator import (
    RWADataAggregator,
    ProtocolYieldData,
    CentrifugeConnector,
    GoldfinchConnector,
    MapleConnector
)

__all__ = [
    "RWADataAggregator",
    "ProtocolYieldData",
    "CentrifugeConnector",
    "GoldfinchConnector",
    "MapleConnector"
]