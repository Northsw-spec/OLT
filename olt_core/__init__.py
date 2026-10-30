"""Versioned OLT multilingual source-first research infrastructure; NO Bible release."""
from .engine import (
    ENGINE_VERSION, CONTRACT_VERSION, SourceContractError,
    validate_source, validate_locale, from_genesis_1_verse,
    make_research_packet, build_genesis_1_1_research_packets,
)
__all__ = [
    "ENGINE_VERSION","CONTRACT_VERSION","SourceContractError","validate_source",
    "validate_locale","from_genesis_1_verse","make_research_packet",
    "build_genesis_1_1_research_packets",
]
