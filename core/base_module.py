from abc import ABC, abstractmethod


class BaseAuditModule(ABC):
    """
    Base interface for all audit modules.
    """

    name = "Base Audit Module"

    @abstractmethod
    def run(self, target="localhost"):
        """
        Execute the audit.

        Args:
            target (str): Hostname, IP address, or domain.

        Returns:
            dict: Audit result.
        """
        raise NotImplementedError
