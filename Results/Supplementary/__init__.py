from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd

# -----------------------------------------------------------------------------------------------------------
# Data paths across tasks

@dataclass
class Ferret():
    """ Metadata associated with a specific subject """
    
    num : int
    name : str

    def __post_init__(self):
        self.fstr = f"F{self.num}"

    def load_data(self, file_path: str) -> None:
        """Import behavioral data from csv file"""

        self.data = pd.read_csv( Path(file_path) / f"{self.fstr}.csv")        
        print(f"{self.fstr}.csv")



@dataclass
class Task(Enum):

    VOWELS_IN_NOISE = 'Results/Vowels_Cooling/data/analysis'
    VOWELS_SPATIAL  = 'Results/Vowels_Unmasking/data/analysis'
    LOCALIZATION    = 'Results/Localization/data/analysis'