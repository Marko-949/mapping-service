from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def get_shop_structure(self, force_refresh: bool = False):
        """Vraća unificirani format: [{'category': 'Ime', 'attributes': [...]}]"""
        pass