from datetime import datetime

from .puzzle import create_puzzle  # noqa: F401
from .puzzle import solve_puzzle  # noqa: F401


__version__ = datetime.today().strftime("%Y.%m.%d")
