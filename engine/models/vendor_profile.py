from dataclasses import dataclass, field
from typing import Dict
from engine1.engine import VendorProfile as LegacyVendorProfile


@dataclass
class VendorProfile:
    vendor: str
    file_name: str
    doc_type: str = "unstructured"
    confidence: str = "medium"
    commercial: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        # Delegate to legacy dataclass when possible
        return {
            "vendor": self.vendor,
            "file_name": self.file_name,
            "doc_type": self.doc_type,
            "confidence": self.confidence,
            "commercial": self.commercial,
        }
