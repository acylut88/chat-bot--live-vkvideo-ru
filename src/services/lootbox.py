import random
from typing import Dict, Any
from src.core.config import LootboxConfig, settings

class LootboxEngine:
    """
    Класс-сервис математического ядра 'Танкового Синдиката'.
    Принимает объект конфигурации, что позволяет легко менять правила игры
    или подсовывать тестовые конфигурации (паттерн Dependency Injection / Внедрение зависимостей).
    """
    def __init__(self, config: LootboxConfig = settings):
        self.cfg = config

    def calculate_drop(self, box_type: str, is_vip: bool, current_opens: int) -> Dict[str, Any]:
        """
        Проводит симуляцию прохождения 6-шаговой цепочки лутбокса.
        Возвращает структурированный словарь с результатами.
        """
        # Проверка лимита открытий за стрим
        if current_opens >= self.cfg.MAX_OPENS_PER_STREAM:
            return {
                "success": False, 
                "error": f"Лимит исчерпан! Вы открыли максимум ({self.cfg.MAX_OPENS_PER_STREAM} боксов) за этот стрим."
            }
            
        # Валидация входного типа бокса
        if box_type not in self.cfg.TIER_MODIFIERS:
            return {"success": False, "error": f"Неизвестный тип бокса: {box_type}"}
            
        tier = self.cfg.TIER_MODIFIERS[box_type]
        
        # Рассчитываем суммарный бонус к шансам (Тир + VIP)
        total_chance_bonus = tier["chance_bonus"] + (0.05 if is_vip else 0.00)
        
        step_reached = 0
        is_exploded = False
        
        # Запускаем цикл прохождения цепочки шагов
        for step in range(1, 7):
            base_chance = self.cfg.BASE_CHANCES[step]
            
            # Итоговый шанс не может превышать 99% (оставляем 1% на контролируемый взрыв)
            final_chance = min(base_chance + total_chance_bonus, 0.99)
            
            # Бросаем случайное число от 0.0 до 1.0 (симуляция кубика / roll)
            if random.random() <= final_chance:
                step_reached = step
            else:
                is_exploded = True
                break # Коробка взорвалась, прерываем прохождение цепочки

        # Рассчитываем финальную награду на основе достигнутого шага
        reward_al = self._calculate_reward_amount(tier["loot_mult"], step_reached, is_vip)

        return {
            "success": True,
            "box_name": tier["label"],
            "user_tier": "premium (VIP)" if is_vip else "normal",
            "step_reached": step_reached,
            "is_exploded": is_exploded,
            "reward_al": reward_al,
            "error": None
        }

    def _calculate_reward_amount(self, loot_mult: float, step_reached: int, is_vip: bool) -> int:
        """
        Внутренний (приватный) инкапсулированный метод расчета награды AL.
        Доступен только внутри этого класса, скрывая детали формулы от внешнего мира.
        """
        if step_reached == 0:
            return 0
            
        # Формула: База (100) * Множитель тира (1.0 / 1.1 / 1.25)
        tier_base = int(self.cfg.GLOBAL_BASE_REWARD * loot_mult)
        
        # Умножаем на прогрессию шага
        calculated_reward = tier_base * self.cfg.STEP_MULTIPLIERS[step_reached]
        
        # Накидываем +50% для VIP-премиум пользователей
        if is_vip:
            calculated_reward *= self.cfg.VIP_LOOT_MULTIPLIER
            
        return int(calculated_reward)
