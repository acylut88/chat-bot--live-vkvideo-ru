import sys
from tests.test_01_logic import run_tests as run_logic_tests
from tests.test_02_db import run_db_tests
from tests.test_03_chat import run_chat_test

def start_application():
    """Главная точка входа для запуска Танкового Синдиката в прод-режиме"""
    print("🚀 Инициализация платформы 'Танковый Синдикат'...")
    print("Проект запущен в промышленном режиме. Ожидание подключения модулей...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1] # Исправлен баг получения аргумента
        if arg == "--test-logic":
            run_logic_tests()
        elif arg == "--test-db":
            run_db_tests()
        elif arg == "--test-chat":
            run_chat_test()
        else:
            print(f"❌ Неизвестный флаг: {arg}. Используйте --test-logic, --test-db или --test-chat")
    else:
        start_application()
