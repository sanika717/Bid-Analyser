from dataclasses import dataclass, field
from typing import Dict

@dataclass
class VendorProfile:
    vendor: str
    commercial: Dict[str, str] = field(default_factory=dict)