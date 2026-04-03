from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def get_shop_structure(self, force_refresh: bool = False):
        """[{'category': 'Ime', 'attributes': [...]}]"""
        pass
    
    @abstractmethod
    def get_categories(self) -> list:
        pass