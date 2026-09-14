import json
import logging
import ssl
import os
from websockets.asyncio.client import connect  
from src.core.config import settings
from src.core.db import AsyncSessionLocal
from src.services.lootbox import LootboxEngine
from src.services.user_db import UserDatabaseService
from src.models.database import LootboxLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyndicateChatWorker")

class ChatWorker:
    """Промышленный асинхронный воркер чата, работающий напрямую через WebSockets."""
    
    def __init__(self):
        self.loot_engine = LootboxEngine()
        self.mock_channel_id = 888888 
        self.msg_id = 1  

    async def start(self):
        if not settings.TEST_CENTRIFUGO_TOKEN:
            logger.error("❌ TEST_CENTRIFUGO_TOKEN не задан в .env!")
            return

        logger.info(f"🔌 Подключение напрямую к сокету: {settings.TEST_CENTRIFUGO_URL}")
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://vkvideo.ru"
        }
        
        cookie_env = os.getenv("TEST_BROWSER_COOKIE") or getattr(settings, "TEST_BROWSER_COOKIE", None)
        if cookie_env:
            browser_headers["Cookie"] = cookie_env

        async with connect(
            settings.TEST_CENTRIFUGO_URL, 
            ssl=ssl_context, 
            additional_headers=browser_headers
        ) as ws:
            
            connect_cmd = {"connect": {"token": settings.TEST_CENTRIFUGO_TOKEN}, "id": self.msg_id}
            self.msg_id += 1
            await ws.send(json.dumps(connect_cmd))
            await ws.recv()
            logger.info("🔐 Авторизация на сервере Centrifugo успешна.")

            subscribe_cmd = {"subscribe": {"channel": settings.TEST_CHAT_TOPIC}, "id": self.msg_id}
            self.msg_id += 1
            await ws.send(json.dumps(subscribe_cmd))
            await ws.recv()
            
            logger.info(f"✅ Успешно подписались на топик чата: {settings.TEST_CHAT_TOPIC}")
            logger.info("🔥 Начинаем бесконечный сбор живых сообщений стрима...")

            async for raw_message in ws:
                try:
                    packet = json.loads(raw_message)
                    
                    if not packet:
                        await ws.send(json.dumps({}))
                        continue
                        
                    if isinstance(packet, dict) and "result" in packet:
                        continue
                        
                    push_data = packet.get("push", {}) if isinstance(packet, dict) else {}
                    pub_data = push_data.get("pub", {})
                    outer_data = pub_data.get("data", {})
                    
                    inner_data = outer_data.get("data", {}) if isinstance(outer_data, dict) else {}
                    if not inner_data:
                        continue
                        
                    user_info = inner_data.get("user", {})
                    vk_id_raw = user_info.get("id")
                    username = user_info.get("nick") or user_info.get("displayName", "Танкист")
                    
                    message_contents = inner_data.get("data", [])
                    
                    # Тихо пропускаем системные уведомления VK (без генерации WARNING)
                    if not vk_id_raw or not message_contents:
                        continue
                        
                    text_parts = []
                    for content_block in message_contents:
                        if content_block.get("type") == "text":
                            content_raw = content_block.get("content", "")
                            try:
                                parsed_array = json.loads(content_raw)
                                if isinstance(parsed_array, list) and len(parsed_array) > 0:
                                    text_parts.append(str(parsed_array))
                                else:
                                    text_parts.append(str(content_raw))
                            except Exception:
                                text_parts.append(str(content_raw))
                        elif content_block.get("type") == "smile":
                            text_parts.append("[Смайл]")

                    text = " ".join(text_parts).strip()
                    if not text or text.startswith("BLOCK_END"):
                        continue

                    vk_id = int(vk_id_raw)
                    
                    words_count = len(text.split())
                    if words_count <= 2:
                        box_type = "cheap"
                    elif 3 <= words_count <= 4:
                        box_type = "normal"
                    else:
                        box_type = "elite"
                    
                    async with AsyncSessionLocal() as session:
                        progress = await UserDatabaseService.process_chat_activity(
                            session=session, vk_id=vk_id, username=username, channel_id=self.mock_channel_id
                        )
                        
                        drop_result = self.loot_engine.simulate_single_opening(
                            box_type=box_type, is_vip=progress.is_vip
                        )
                        
                        if drop_result["success"]:
                            progress.ac_balance += drop_result["reward_al"]
                            
                            log_record = LootboxLog(
                                vk_id=vk_id, channel_id=self.mock_channel_id, session_id=1,
                                box_type=box_type, step_reached=drop_result["step_reached"],
                                is_exploded=drop_result["is_exploded"], reward_al=drop_result["reward_al"]
                            )
                            session.add(log_record)
                            await session.commit()
                            
                            logger.info(
                                f"💬 [{username} | ID: {vk_id}]: {text[:35]}... -> Слов: {words_count} -> "
                                f"Удача: {box_type} (Шаг {drop_result['step_reached']}/6) -> +{drop_result['reward_al']} AL (Баланс: {progress.ac_balance})"
                            )
                except Exception:
                    pass
