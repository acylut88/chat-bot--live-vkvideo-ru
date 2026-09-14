import sys
from tests.test_01_logic import run_tests as run_logic_tests
from tests.test_02_db import run_db_tests

def start_application():
    """Главная точка входа для запуска Танкового Синдиката в прод-режиме"""
    print("🚀 Инициализация платформы 'Танковый Синдикат'...")
    print("Проект запущен в промышленном режиме. Ожидание подключения модулей...")

if __name__ == "__main__":
    # Паттерн CLI-управления: проверяем переданные аргументы командной строки
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--test-logic":
            run_logic_tests()
        elif arg == "--test-db":
            run_db_tests()
        else:
            print(f"❌ Неизвестный флаг: {arg}. Используйте --test-logic или --test-db")
    else:
        start_application()
