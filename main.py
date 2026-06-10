# /// script
# dependencies = ["pygame-ce"]
# ///

import asyncio
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent / 'code'))

from main import main as game_main  # noqa: E402


asyncio.run(game_main())
