import asyncio
from typing import Dict
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import Plain
from astrbot.core.message.message_event_result import MessageChain
from astrbot.core.provider.entities import LLMResponse, ProviderRequest

@register("astrbot_plugin_sync_group_chat", "ctrlkk", "让AstrBot以同步队列的方式处理消息", "0.1")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        self.queues: Dict[str, asyncio.Queue] = {}

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
    
    @filter.on_llm_request()
    async def my_custom_hook_1(self, event: AstrMessageEvent, req: ProviderRequest):
        """请求开始"""
        session_id = event.session_id
        queue = self.queues.get(session_id)
        if not queue:
            queue = asyncio.Queue(1)
            self.queues[session_id] = queue
        await queue.put(req)
        logger.info(f"{session_id}开始执行")

    @filter.on_llm_response()
    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse):
        """请求结束"""
        session_id = event.session_id
        queue = self.queues.get(session_id)
        if queue:
            await queue.get()
            logger.info(f"{session_id}结束")
