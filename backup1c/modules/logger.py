"""
Модуль настройки логирования с цветным выводом и ротацией файлов
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

import colorlog


def setup_logger(
    name: str,
    log_dir: Path,
    level: int = logging.INFO,
    console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Настройка логгера с цветным выводом в консоль и ротацией файлов
    
    Args:
        name: Имя логгера
        log_dir: Директория для файлов логов
        level: Уровень логирования
        console: Выводить ли в консоль
        max_bytes: Максимальный размер файла лога
        backup_count: Количество резервных копий логов
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем директорию для логов
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Файловый обработчик с ротацией
    log_file = log_dir / f"{name.replace('.', '_')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Консольный обработчик с цветами
    if console:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


class BackupLogger:
    """Специализированный логгер для операций резервного копирования"""
    
    def __init__(self, base_name: str, log_dir: Path):
        """
        Инициализация логгера для конкретной базы
        
        Args:
            base_name: Имя базы данных
            log_dir: Директория для логов
        """
        self.base_name = base_name
        self.log_dir = Path(log_dir)
        self.logger = setup_logger(f"backup.{base_name}", self.log_dir)
        
        # Создаем отдельный лог-файл для текущей сессии
        session_log = self.log_dir / f"backup_{base_name}_{datetime.now():%Y%m%d_%H%M%S}.log"
        self.session_handler = logging.FileHandler(session_log, encoding='utf-8')
        self.session_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(self.session_handler)
        self.session_log_path = session_log
        
    def info(self, message: str) -> None:
        """Логирование информационного сообщения"""
        self.logger.info(f"[{self.base_name}] {message}")
        
    def warning(self, message: str) -> None:
        """Логирование предупреждения"""
        self.logger.warning(f"[{self.base_name}] {message}")
        
    def error(self, message: str, exc_info: bool = False) -> None:
        """Логирование ошибки"""
        self.logger.error(f"[{self.base_name}] {message}", exc_info=exc_info)
        
    def debug(self, message: str) -> None:
        """Логирование отладочного сообщения"""
        self.logger.debug(f"[{self.base_name}] {message}")
        
    def critical(self, message: str, exc_info: bool = True) -> None:
        """Логирование критической ошибки"""
        self.logger.critical(f"[{self.base_name}] {message}", exc_info=exc_info)
        
    def cleanup(self) -> None:
        """Очистка обработчиков и закрытие файлов"""
        if self.session_handler:
            self.session_handler.close()
            self.logger.removeHandler(self.session_handler)
            
    def get_session_log_content(self) -> Optional[str]:
        """Получение содержимого лога текущей сессии"""
        try:
            if self.session_log_path.exists():
                return self.session_log_path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Не удалось прочитать лог сессии: {e}")
        return None