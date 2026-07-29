from typing import Dict, Any, List, Optional
import logging
from src.domain.solutions.base_solution import ISolutionPack
from src.infrastructure.solutions.legal_pack import LegalSolutionPack
from src.infrastructure.solutions.finance_pack import FinanceSolutionPack
from src.infrastructure.solutions.hr_pack import HRSolutionPack

logger = logging.getLogger("document_intelligence.solution_registry")


class SolutionPackRegistry:
    """Centralized Registry for Enterprise Industry Solution Packs."""

    _packs: Dict[str, ISolutionPack] = {}

    @classmethod
    def register_pack(cls, pack: ISolutionPack):
        info = pack.pack_info()
        cls._packs[info["pack_id"]] = pack
        logger.info(f"Registered Industry Solution Pack: '{info['pack_id']}' ({info['name']})")

    @classmethod
    def get_pack(cls, pack_id: str) -> Optional[ISolutionPack]:
        return cls._packs.get(pack_id)

    @classmethod
    def list_packs(cls) -> List[Dict[str, Any]]:
        return [p.pack_info() for p in cls._packs.values()]


# Auto-register Default Built-in Solution Packs
SolutionPackRegistry.register_pack(LegalSolutionPack())
SolutionPackRegistry.register_pack(FinanceSolutionPack())
SolutionPackRegistry.register_pack(HRSolutionPack())
