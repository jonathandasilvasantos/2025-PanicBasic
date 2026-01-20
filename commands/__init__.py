"""
PASIC Command Handler Modules

This package contains mixin classes that provide command handlers for the
BasicInterpreter. Each mixin provides a category of related commands.

Available mixins:
- AudioCommandsMixin: BEEP, SOUND, PLAY commands
"""

from commands.audio import AudioCommandsMixin

__all__ = ['AudioCommandsMixin']
