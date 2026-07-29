from abc import ABC, abstractmethod


class IVirusScanner(ABC):
    """Abstract contract for security anti-virus scanners (e.g. ClamAV)."""

    @abstractmethod
    async def scan_bytes(self, data: bytes, filename: str = "upload") -> bool:
        """
        Scan binary content for malware/viruses.
        Returns True if clean, raises ValueError/SecurityError if infected.
        """
        pass


class MockVirusScanner(IVirusScanner):
    """Production-ready mock virus scanner for development and test environments."""

    async def scan_bytes(self, data: bytes, filename: str = "upload") -> bool:
        # Check for EICAR test string signature
        EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        if EICAR_SIGNATURE in data:
            raise ValueError(f"Security Alert: Malware signature detected in file '{filename}'.")
        return True
