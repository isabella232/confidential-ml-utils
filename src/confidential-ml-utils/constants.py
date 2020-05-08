from enum import Enum

class DataCategory(Enum):
    CONTAINS_PRIVATE_DATA = 1  # data contains confidential or otherwise potentially private data
    ONLY_PUBLIC_DATA = 2 # logged data only contains numbers or messages, no private data is present
