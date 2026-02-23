"""
Queue-First Small Talk Twin — stillwater/admin/orchestration/smalltalk/

Architecture:
  User input
    → BanterQueueDB.get_next()     (< 5ms SLA — queue hit)
    → SmallTalkCPU.detect_glow()   (< 50ms SLA — CPU fallback)
    → WarmToken returned to caller

Public surface:
    from stillwater.admin.orchestration.smalltalk import SmallTalkCPU
    from stillwater.admin.orchestration.smalltalk.models import (
        RegisterProfile, BanterQueueEntry, WarmToken
    )
    from stillwater.admin.orchestration.smalltalk.database import BanterQueueDB

No network. No ML. No randomness. rung_target: 641.
"""

from .cpu import SmallTalkCPU
from .database import BanterQueueDB, JokeRepo, PatternRepo, TechFactRepo
from .models import (
    BanterQueueEntry,
    JokeEntry,
    RegisterProfile,
    SmallTalkPattern,
    TechFactEntry,
    WarmToken,
    WeatherContext,
)
from .weather_banter import generate_weather_banter

__all__ = [
    # Core classes
    "SmallTalkCPU",
    "BanterQueueDB",
    "JokeRepo",
    "TechFactRepo",
    "PatternRepo",
    # Models
    "RegisterProfile",
    "SmallTalkPattern",
    "BanterQueueEntry",
    "WarmToken",
    "JokeEntry",
    "TechFactEntry",
    "WeatherContext",
    # Functions
    "generate_weather_banter",
]
