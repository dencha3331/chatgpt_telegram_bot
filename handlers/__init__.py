from .user_handlers import *
from .other_handlers import *
from .registration_handlers import *
from handlers.voice_handlers import *
from handlers.weather_handlers import *


__all__ = (
    'user_handler_router',
    'registration_router',
    'voice_router',
    'weather_router',
)


