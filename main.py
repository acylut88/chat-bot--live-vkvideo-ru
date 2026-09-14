import sys
from tests.test_logic import run_tests

def start_application():
    """Главная точка входа для запуска Танкового Синдиката"""
    print("🚀 Инициализация платформы 'Танковый Синдикат'...")
    print("Проект запущен в промышленном режиме. Ожидание подключения модулей...")
    # Здесь в будущем будет запускаться FastAPI-сервер и асинхронные таски чата

if __name__ == "__main__":
    # Паттерн CLI-управления: если запускаем с флагом --test, то прогоняем тесты
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        start_application()
