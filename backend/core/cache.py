import json
from typing import Dict, List

import redis.asyncio as redis

from core import settings
from views.actions import ActionView


class Cache:
    def __init__(self, host=settings.REDIS_HOST):
        self.conn = redis.from_url(f"redis://{host}")


class ActionCache(Cache):
    max_actions_length = 30
    key = "actions"

    async def get_all_actions(self) -> List[Dict]:
        stored_data = await self.conn.lrange(self.key, 0, -1)
        return [json.loads(item) for item in stored_data]

    async def insert(self, value: ActionView):
        await self.conn.lpush(self.key, value.json())
        await self.conn.ltrim(self.key, 0, self.max_actions_length)

    async def update_status(self, message_id, status):
        actions = await self.get_all_actions()
        for idx, item in enumerate(actions):
            action = ActionView(**item)
            if action.message_id == message_id:
                action.status = status
                await self.conn.lset(self.key, idx, action.json())
