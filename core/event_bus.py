import asyncio

class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, event_data: dict):
        await self.queue.put(event_data)

    async def subscribe(self):
        while True:
            yield await self.queue.get()
            self.queue.task_done()

# 全域單例
event_bus = EventBus()