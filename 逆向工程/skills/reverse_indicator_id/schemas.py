"""Data schemas for reverse indicator ID skill."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IndicatorInput:
    """Raw indicator to be reverse-engineered."""

    raw_indicator_code: str
    current_meaning: str
    remark: str = ""
    # From CSV or supplemental metadata
    indicator_name: str = ""
    unit: str = ""
    adjustment: str = ""
    source: str = ""
    data_type: str = ""


@dataclass
class RoundResult:
    """Result from a single round of reverse engineering."""

    recommended_indicator_id: str = ""
    alternative_indicator_ids: list[str] = field(default_factory=list)
    confidence: str = ""  # high / medium / low
    display_name_cn: str = ""
    naming_rationale_short: str = ""
    raw_response: str = ""


@dataclass
class ReverseResult:
    """Final result combining both rounds."""

    raw_indicator_code: str = ""
    current_meaning: str = ""
    indicator_name: str = ""
    unit: str = ""
    adjustment: str = ""
    source: str = ""
    data_type: str = ""
    remark: str = ""
    # Round results
    round1_indicator_id: str = ""
    round1_alternatives: list[str] = field(default_factory=list)
    round1_confidence: str = ""
    round1_raw_response: str = ""
    round2_indicator_id: str = ""
    round2_alternatives: list[str] = field(default_factory=list)
    round2_confidence: str = ""
    round2_raw_response: str = ""
    # Comparison
    consistency: str = ""  # high / medium / low
    final_indicator_id: str = ""
    final_confidence: str = ""
    notes: str = ""

    def to_json_dict(self) -> dict:
        return {
            "raw_indicator_code": self.raw_indicator_code,
            "current_meaning": self.current_meaning,
            "indicator_name": self.indicator_name,
            "unit": self.unit,
            "adjustment": self.adjustment,
            "source": self.source,
            "data_type": self.data_type,
            "remark": self.remark,
            "round1_indicator_id": self.round1_indicator_id,
            "round1_alternatives": self.round1_alternatives,
            "round1_confidence": self.round1_confidence,
            "round1_raw_response": self.round1_raw_response,
            "round2_indicator_id": self.round2_indicator_id,
            "round2_alternatives": self.round2_alternatives,
            "round2_confidence": self.round2_confidence,
            "round2_raw_response": self.round2_raw_response,
            "consistency": self.consistency,
            "final_indicator_id": self.final_indicator_id,
            "final_confidence": self.final_confidence,
            "notes": self.notes,
        }

    def to_csv_dict(self) -> dict:
        return {
            "raw_indicator_code": self.raw_indicator_code,
            "current_meaning": self.current_meaning,
            "unit": self.unit,
            "adjustment": self.adjustment,
            "source": self.source,
            "data_type": self.data_type,
            "round1_indicator_id": self.round1_indicator_id,
            "round2_indicator_id": self.round2_indicator_id,
            "consistency": self.consistency,
            "final_indicator_id": self.final_indicator_id,
            "final_confidence": self.final_confidence,
            "notes": self.notes,
        }
