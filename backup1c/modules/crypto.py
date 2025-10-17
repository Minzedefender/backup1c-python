"""
Модуль шифрования секретов (токенов, паролей) с использованием Fernet (AES)
"""

import json
from pathlib import Path
from typing import Dict, Any

from cryptography.fernet import Fernet, InvalidToken

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backup1c.core.exceptions import CryptoError


class SecretsManager:
    """Менеджер для шифрования и дешифрования секретов"""
    
    def __init__(self, key_path: Path):
        """
        Инициализация менеджера секретов
        
        Args:
            key_path: Путь к файлу с ключом шифрования
        """
        self.key_path = Path(key_path)
        self._ensure_key()
        
    def _ensure_key(self) -> None:
        """Создание ключа шифрования, если он не существует"""
        if not self.key_path.exists():
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
            # Устанавливаем ограниченные права доступа
            try:
                import os
                os.chmod(self.key_path, 0o600)
            except Exception:
                pass  # Игнорируем ошибки chmod на Windows
                
    def _get_cipher(self) -> Fernet:
        """Получение объекта шифрования"""
        try:
            key = self.key_path.read_bytes()
            return Fernet(key)
        except Exception as e:
            raise CryptoError(f"Не удалось загрузить ключ шифрования: {e}")
            
    def encrypt_secrets(self, secrets: Dict[str, Any], output_path: Path) -> None:
        """
        Шифрование секретов в файл
        
        Args:
            secrets: Словарь с секретами для шифрования
            output_path: Путь к выходному файлу
            
        Raises:
            CryptoError: При ошибке шифрования
        """
        try:
            cipher = self._get_cipher()
            
            # Конвертируем в JSON
            json_data = json.dumps(secrets, ensure_ascii=False, indent=2)
            
            # Шифруем
            encrypted = cipher.encrypt(json_data.encode('utf-8'))
            
            # Сохраняем
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(encrypted)
            
        except Exception as e:
            raise CryptoError(f"Ошибка при шифровании секретов: {e}")
            
    def decrypt_secrets(self, input_path: Path) -> Dict[str, Any]:
        """
        Дешифрование секретов из файла
        
        Args:
            input_path: Путь к зашифрованному файлу
            
        Returns:
            Словарь с дешифрованными секретами
            
        Raises:
            CryptoError: При ошибке дешифрования
        """
        if not input_path.exists():
            return {}
            
        try:
            cipher = self._get_cipher()
            
            # Читаем зашифрованные данные
            encrypted = input_path.read_bytes()
            
            # Дешифруем
            decrypted = cipher.decrypt(encrypted)
            
            # Парсим JSON
            return json.loads(decrypted.decode('utf-8'))
            
        except InvalidToken:
            raise CryptoError("Неверный ключ шифрования или поврежденный файл секретов")
        except json.JSONDecodeError as e:
            raise CryptoError(f"Ошибка парсинга секретов: {e}")
        except Exception as e:
            raise CryptoError(f"Ошибка при дешифровании секретов: {e}")
            
    def update_secret(self, secrets_path: Path, key: str, value: str) -> None:
        """
        Обновление одного секрета
        
        Args:
            secrets_path: Путь к файлу секретов
            key: Ключ секрета
            value: Значение секрета
        """
        secrets = self.decrypt_secrets(secrets_path)
        secrets[key] = value
        self.encrypt_secrets(secrets, secrets_path)
        
    def remove_secret(self, secrets_path: Path, key: str) -> None:
        """
        Удаление секрета
        
        Args:
            secrets_path: Путь к файлу секретов
            key: Ключ секрета для удаления
        """
        secrets = self.decrypt_secrets(secrets_path)
        if key in secrets:
            del secrets[key]
            self.encrypt_secrets(secrets, secrets_path)
            
    def get_secret(self, secrets_path: Path, key: str, default: Any = None) -> Any:
        """
        Получение одного секрета
        
        Args:
            secrets_path: Путь к файлу секретов
            key: Ключ секрета
            default: Значение по умолчанию
            
        Returns:
            Значение секрета или default
        """
        secrets = self.decrypt_secrets(secrets_path)
        return secrets.get(key, default)