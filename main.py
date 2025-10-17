#!/usr/bin/env python3
"""
Backup1C - Система резервного копирования баз данных 1С
Точка входа приложения

Использование:
    python main.py              # Запуск GUI
    python main.py --cli        # Запуск CLI
    python main.py --help       # Справка
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь для импорта
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

__version__ = "1.0.0"


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Backup1C - Система резервного копирования баз данных 1С",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                      # Запуск GUI
  python main.py --cli                # Запуск CLI
  python main.py --version            # Показать версию
  
Для помощи по CLI командам:
  python main.py --cli --help
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Запустить в режиме командной строки (без GUI)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Backup1C v{__version__}'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Включить режим отладки'
    )
    
    parser.add_argument(
        '--config-dir',
        type=Path,
        default=ROOT_DIR / 'config',
        help='Путь к директории конфигурации (по умолчанию: config/)'
    )
    
    return parser.parse_known_args()


def setup_logging(debug: bool = False):
    """Настройка базового логирования"""
    import logging
    
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger('backup1c')


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 9):
        print("ОШИБКА: Требуется Python 3.9 или выше")
        print(f"Текущая версия: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("\nСкачайте последнюю версию с https://www.python.org/downloads/")
        sys.exit(1)


def run_gui(config_dir: Path, debug: bool = False):
    """Запуск графического интерфейса"""
    logger = setup_logging(debug)
    
    try:
        logger.info("Запуск GUI режима...")
        
        # Проверяем наличие Dear PyGui
        try:
            import dearpygui.dearpygui as dpg
        except ImportError:
            print("\n" + "="*60)
            print("ОШИБКА: Библиотека Dear PyGui не установлена!")
            print("="*60)
            print("\nУстановите зависимости:")
            print("  pip install -r requirements.txt")
            print("\nИли установите Dear PyGui отдельно:")
            print("  pip install dearpygui>=1.10.1")
            print("="*60 + "\n")
            sys.exit(1)
        
        # TODO: Импортировать GUI приложение когда оно будет готово
        # from backup1c.gui.app import main as gui_main
        # return gui_main(config_dir=config_dir)
        
        # Временная заглушка
        print("\n" + "="*60)
        print("🎨 GUI РЕЖИМ (В РАЗРАБОТКЕ)")
        print("="*60)
        print(f"\nВерсия: {__version__}")
        print(f"Директория конфигурации: {config_dir}")
        print(f"Режим отладки: {'Включен' if debug else 'Выключен'}")
        print("\n💡 GUI интерфейс находится в разработке")
        print("   Используйте CLI режим: python main.py --cli")
        print("="*60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nПрервано пользователем")
        return 0
    except Exception as e:
        logger.error(f"Критическая ошибка в GUI: {e}", exc_info=True)
        return 1


def run_cli(args, config_dir: Path, debug: bool = False):
    """Запуск CLI интерфейса"""
    logger = setup_logging(debug)
    
    try:
        logger.info("Запуск CLI режима...")
        
        # TODO: Импортировать CLI приложение когда оно будет готово
        # from backup1c.cli.commands import cli
        # sys.argv = [sys.argv[0]] + args
        # return cli()
        
        # Временная заглушка
        print("\n" + "="*60)
        print("⌨️  CLI РЕЖИМ (В РАЗРАБОТКЕ)")
        print("="*60)
        print(f"\nВерсия: {__version__}")
        print(f"Директория конфигурации: {config_dir}")
        print(f"Режим отладки: {'Включен' if debug else 'Выключен'}")
        print("\n💡 CLI интерфейс находится в разработке")
        print("\nДоступные команды (планируется):")
        print("  backup              - Запуск резервного копирования")
        print("  setup               - Мастер первичной настройки")
        print("  list                - Список настроенных баз")
        print("  schedule            - Управление расписанием")
        print("="*60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nПрервано пользователем")
        return 0
    except Exception as e:
        logger.error(f"Критическая ошибка в CLI: {e}", exc_info=True)
        return 1


def main():
    """Главная функция запуска приложения"""
    
    # Проверка версии Python
    check_python_version()
    
    # Парсинг аргументов
    args, unknown_args = parse_arguments()
    
    # Создание директорий
    args.config_dir.mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / 'logs').mkdir(parents=True, exist_ok=True)
    
    # Приветствие
    if not args.cli:
        print(f"\n{'='*60}")
        print(f"  Backup1C v{__version__}")
        print(f"  Система резервного копирования баз данных 1С")
        print(f"{'='*60}\n")
    
    # Выбор режима запуска
    if args.cli or unknown_args:
        return run_cli(unknown_args, args.config_dir, args.debug)
    else:
        return run_gui(args.config_dir, args.debug)


if __name__ == '__main__':
    sys.exit(main())