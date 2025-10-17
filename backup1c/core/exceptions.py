"""
Кастомные исключения для системы резервного копирования Backup1C
"""


class Backup1CException(Exception):
    """Базовое исключение для всех ошибок Backup1C"""
    pass


class ConfigurationError(Backup1CException):
    """Ошибка конфигурации"""
    pass


class BackupError(Backup1CException):
    """Ошибка при выполнении резервного копирования"""
    pass


class CloudError(Backup1CException):
    """Ошибка при работе с облачным хранилищем"""
    pass


class TelegramError(Backup1CException):
    """Ошибка при отправке уведомления в Telegram"""
    pass


class OneCError(Backup1CException):
    """Ошибка при работе с 1С конфигуратором"""
    pass


class ServiceError(Backup1CException):
    """Ошибка при работе со службами Windows"""
    pass


class CryptoError(Backup1CException):
    """Ошибка при шифровании/дешифровании"""
    pass


class ValidationError(Backup1CException):
    """Ошибка валидации данных"""
    pass


class SchedulerError(Backup1CException):
    """Ошибка планировщика задач"""
    pass