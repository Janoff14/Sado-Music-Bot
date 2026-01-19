"""Run the Sado Music Bot"""
import asyncio
import sys
print("Python version:", sys.version)
print("Starting bot...")

from sado_music_bot.app import main
asyncio.run(main())

