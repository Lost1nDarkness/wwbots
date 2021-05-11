#!/usr/bin/env python3

# Copyright 2021 PeechezNCreem
# Licensed under the GPL 3.0.

import asyncio
import signal

from wizwalker import WizWalker
from wizwalker.combat.handler import CombatHandler


# https://github.com/PeechezNCreem/peechutils
class InterruptBlocker:
    """Blocks keyboard interrupt signals within its scope."""

    def __init__(self):
        self.original_handler = signal.getsignal(signal.SIGINT)

    def __enter__(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        return self

    def __exit__(self, *args):
        signal.signal(signal.SIGINT, self.original_handler)


class AOESpammer(CombatHandler):
    async def handle_round(self):
        if not (cards := await self.get_cards()):
            raise RuntimeError("No cards found")
        await cards[0].cast(None)


class Bot:
    def __init__(self):
        self.walker = WizWalker()
        self.client = self.walker.get_new_clients()[0]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        with InterruptBlocker():
            asyncio.run(self.walker.close())

    async def activate_hooks(self):
        with InterruptBlocker():
            await self.client.activate_hooks(wait_for_ready=False)
            await self.client.mouse_handler.activate_mouseless()

    async def run(self):
        await self.activate_hooks()
        while True:
            # Enter Rattlebones' tower ("The Archives")
            await self.client.goto(-16510, 19100)
            await self.wait_for_zone_change()

            # Fight Rattlebones
            await self.client.goto(486, -398)
            await AOESpammer(self.client).wait_for_combat()

            # Exit tower
            await self.client.goto(0, -1250)
            await self.wait_for_zone_change()

    async def wait_for_zone_change(self):
        while not await self.client.is_loading():
            await asyncio.sleep(0.1)
        while await self.client.is_loading():
            await asyncio.sleep(0.1)


with Bot() as bot:
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        pass  # suppress KeyboardInterrupt traceback
