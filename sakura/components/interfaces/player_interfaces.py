from abc import ABC, abstractmethod
from qfluentwidgets import ListWidget

class IPlayerContainer(ABC):
    @abstractmethod
    def get_file_list_box(self) -> ListWidget:
        pass 