Привет! Мы разрабатываем пет-проект интерактивного бота на Python (FastAPI, SQLAlchemy, SQLite, WebSockets) для стримов по игре Tanks Blitz (Леста) на платформе VK Видео Лайв. 

Проект называется «Танковый Синдикат». Его цель — удержание аудитории, геймификация и монетизация стрима.

Контекст, логика экосистемы и ТЗ проекта, с которых мы продолжаем разработку:

1. СИСТЕМА ДВУХ ВАЛЮТ:
- Баллы Канала (БК): Базовая валюта VK Видео (320 БК/час). Тратится зрителями на запуск лутбокса (цена: 250 БК) и ставки.
- АциЛУТы (AL): Премиум-валюта бота. Хранится в БД, переносится между стримами, облагается налогами. AL автоматически зачисляются на счет финального Аукциона (Розыгрыша према, голды, танков) в конце стрима.

2. МЕХАНИКА ЛУТБОКСА (ЦЕПОЧКА ИЗ 6 ШАГОВ):
- Стоимость: 250 БК. КД: 10 минут. Общий шанс пройти всю цепочку — 7.07%.
- Начисление AL идет по последнему успешно открытому шагу (если взорвался на следующем — предыдущая награда сохраняется):
  * Шаг 1 (100%): +50 AL (Премиум бокс: +100 AL, шансы - 100%)
  * Шаг 2 (95%): +100 AL (Премиум бокс: +200 AL, шансы - 99%)
  * Шаг 3 (85%): +200 AL (Премиум бокс: +400 AL, шансы - 95%)
  * Шаг 4 (70%): +400 AL (Премиум бокс: +800 AL, шансы - 85%)
  * Шаг 5 (50%): +800 AL (Премиум бокс: +1500 AL, шансы - 70%)
  * Шаг 6 (25%): +1500 AL (Премиум бокс: +2500 AL, шансы - 50%)

3. ДОПОЛНИТЕЛЬНЫЙ ФАРМ AL:
- Ставки на исход боя стримера через БК в VK. Угадал (!победа/!слив) -> +100 AL.
- Бонус «Победный Взвод»: Если стример берет в бою «Мастера», весь активный чат получает +50 AL.
- Донат-буст: 1 рубль = 5 AL (Монетизация).

4. МЯГКАЯ СИСТЕМА НАЛОГОВ И ВИНСТРИКОВ (КОНЕЦ СТРИМА):
Дебафф применяется в конце стрима ко всем, кто ничего не выиграл (ТОП-1 сбрасывает баланс в 0, ТОП-2/3 теряют 80%, рандом-победители теряют 60%).
- Минимальный вычет = 100 AL (чтобы балансы не застаивались).
- Условие зачета визита: Зритель обязан открыть минимум 2 лутбокса за стрим (защита от АФК).
- Шкала винстрика посещаемости (подряд) для обычных зрителей:
  * 1-й стрим подряд: дебафф 20%
  * 2-й стрим подряд: дебафф 18%
  * 3-й стрим подряд: дебафф 15%
  * 4+ стримов подряд: ранг [СТАТИСТ] (фиолетовый ник в OBS) -> дебафф всего 10%.
- VIP-статус: Всегда дебафф 10% (даже при прогулах).
- Штрафы за прогулы (для обычных): Пропуск 1 стрима -> серия сгорает, дебафф 20%. Пропуск 2 стримов -> дебафф 50%. Пропуск 3+ стримов -> баланс AL сгорает в 0.

5. МИКРОСЕРВИСНАЯ АРХИТЕКТУРА И СТРУКТУРА БД (SQLAlchemy):
Мы привязываем всё к железному цифровому `vk_id`, который берется из JSON-событий чата WebSocket Centrifugo от VK Video API (чтобы баланс не терялся при смене ников). Также закладываем поле под `lesta_account_id` для будущей интеграции с API Танков.

Вот готовая модель базы данных (models.py), от которой мы отталкиваемся:
```python
import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    vk_id = Column(BigInteger, primary_key=True, autoincrement=False) 
    current_username = Column(String, nullable=False)                 
    lesta_account_id = Column(BigInteger, nullable=True, unique=True) 
    lesta_nickname = Column(String, nullable=True)                    
    ac_balance = Column(Integer, default=0, nullable=False)           
    is_vip = Column(Boolean, default=False, nullable=False)           
    visit_streak = Column(Integer, default=0, nullable=False)         
    last_stream_id = Column(Integer, default=0, nullable=False)       
    stream_reward_status = Column(String, default='none', nullable=False) 

    box_logs = relationship("LootboxLog", back_populates="user", cascade="all, delete-orphan")

class LootboxLog(Base):
    __tablename__ = 'lootbox_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(BigInteger, ForeignKey('users.vk_id', ondelete="CASCADE"), nullable=False)
    stream_id = Column(Integer, nullable=False)                       
    step_reached = Column(Integer, nullable=False)                    
    is_exploded = Column(Boolean, nullable=False)                     
    opened_at = Column(DateTime, default=datetime.datetime.utcnow)    

    user = relationship("User", back_populates="box_logs")
```

Мы готовы продолжить разработку. Предложи, с какого шага нам сейчас лучше начать: написать асинхронный сервис обработки логов лутбоксов и математического ядра (`logic.py`), или реализовать парсер JSON-событий чата для регистрации железных `vk_id`?
