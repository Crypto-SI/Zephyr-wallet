#!/usr/bin/env python3
import json
import asyncio

from zephyr_code.simple_config import SimpleConfig
from zephyr_code.network import filter_version, Network
from zephyr_code.util import create_and_start_event_loop, log_exceptions
from zephyr_code import constants

# testnet?
#constants.set_testnet()
config = SimpleConfig({'testnet': False})

loop, stopping_fut, loop_thread = create_and_start_event_loop()
network = Network(config)
network.start()

@log_exceptions
async def f():
    try:
        peers = await network.get_peers()
        peers = filter_version(peers)
        print(json.dumps(peers, sort_keys=True, indent=4))
    finally:
        stopping_fut.set_result(1)

asyncio.run_coroutine_threadsafe(f(), loop)
