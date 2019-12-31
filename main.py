import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from .jjigae.core import load

load()
