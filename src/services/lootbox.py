import random
from typing import Dict, Any, List
from src.core.config import Settings, settings

class LootboxEngine:
    """
    Бизнес-логика обработки лутбоксов.
    Реализует расчет атомарных открытий и агрегацию финальных наград за стрим.
    """
    def __init__(self, config: Settings = settings):
        self.cfg = config

    def simulate_single_opening(self, box_type: str, is_vip: bool) -> Dict[str, Any]:
        """
        Симулирует мгновенное прохождение всей цепочки из 6 шагов до первого взрыва.
        Возвращает 'сырой' результат этого открытия.
        """
        if box_type not in self.cfg.TIER_CONFIG:
            return {"success": False, "error": f"Неизвестный тип бокса: {box_type}"}
            
        tier = self.cfg.TIER_CONFIG[box_type]
        
        # Рассчитываем суммарный бонус удачи (модификатор тира + VIP статус)
        total_chance_bonus = tier["chance_bonus"] + (0.05 if is_vip else 0.00)
        
        step_reached = 0
        is_exploded = False
        
        # Просчитываем шаги цепочки
        for step in range(1, 7):
            base_chance = self.cfg.BASE_CHANCES[step]
            # Защита: шанс не может быть выше 99%
            final_chance = min(base_chance + total_chance_bonus, 0.99)
            
            if random.random() <= final_chance:
                step_reached = step
            else:
                is_exploded = True
                break # Бокс взорвался на этом шаге
                
        # Вычисляем награду за этот конкретный бокс
        reward_al = self._calculate_box_reward(tier["loot_mult"], step_reached, is_vip)

        return {
            "success": True,
            "box_name": tier["label"],
            "user_tier": "premium (VIP)" if is_vip else "normal",
            "step_reached": step_reached,
            "is_exploded": is_exploded,
            "reward_al": reward_al,
            "error": None
        }

    def aggregate_stream_rewards(self, box_results: List[Dict[str, Any]]) -> int:
        """
        Агрегирует результаты всех открытий зрителя за стрим.
        Применяет выбранный стримером режим начисления (ABSOLUTE_MAX, TOTAL_ACCUMULATIVE, STEP_ACCUMULATIVE).
        """
        if not box_results:
            return 0
            
        mode = self.cfg.REWARD_SYSTEM_MODE
        
        # Режим 1: Складываем абсолютно все награды из всех попыток
        if mode == "TOTAL_ACCUMULATIVE":
            return sum(box["reward_al"] for box in box_results)
            
        # Режим 2: Выбираем одну самую лучшую попытку из всех
        elif mode == "ABSOLUTE_MAX":
            return max(box["reward_al"] for box in box_results)
            
        # Режим 3: Накопительный по шагам внутри бокса, но берется макс. бокс за стрим
        elif mode == "STEP_ACCUMULATIVE":
            # Для этого режима нам нужно сымитировать, сколько принес бы бокс,
            # если бы мы складывали шаги внутри него.
            accumulated_boxes = []
            for box in box_results:
                # Извлекаем данные для пересчета
                box_name_reversed = [k for k, v in self.cfg.TIER_CONFIG.items() if v["label"] == box["box_name"]]
                if not box_name_reversed:
                    continue
                b_type = box_name_reversed[0]
                is_vip = box["user_tier"] == "premium (VIP)"
                
                # Складываем награды за ВСЕ успешно пройденные шаги внутри этого бокса
                box_sum = 0
                for step in range(1, box["step_reached"] + 1):
                    box_sum += self._calculate_box_reward(self.cfg.TIER_CONFIG[b_type]["loot_mult"], step, is_vip)
                accumulated_boxes.append(box_sum)
                
            return max(accumulated_boxes) if accumulated_boxes else 0
            
        return 0

    def _calculate_box_reward(self, loot_mult: float, step_reached: int, is_vip: bool) -> int:
        """Внутренний расчет чистой награды по формуле 'Мягкого фарма' за конкретный шаг."""
        if step_reached == 0:
            return 0
            
        tier_base = int(self.cfg.GLOBAL_BASE_REWARD * loot_mult)
        calculated_reward = tier_base * self.cfg.STEP_MULTIPLIERS[step_reached]
        
        if is_vip:
            calculated_reward *= self.cfg.VIP_LOOT_MULTIPLIER
            
        return int(calculated_reward)
