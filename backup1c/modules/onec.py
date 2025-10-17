"""
Модуль для работы с 1С:Предприятие (конфигуратор)
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backup1c.core.exceptions import OneCError


logger = logging.getLogger(__name__)


class OneCConfigurator:
    """Класс для работы с конфигуратором 1С"""
    
    def __init__(self, exe_path: Path):
        """
        Инициализация конфигуратора
        
        Args:
            exe_path: Путь к 1cestart.exe
            
        Raises:
            OneCError: Если исполняемый файл не найден
        """
        self.exe_path = Path(exe_path)
        
        if not self.exe_path.exists():
            raise OneCError(f"1cestart.exe не найден: {self.exe_path}")
            
        if not self.exe_path.name.lower() == '1cestart.exe':
            raise OneCError(f"Ожидается 1cestart.exe, получен: {self.exe_path.name}")
            
    def export_dt(
        self,
        base_path: Path,
        output_file: Path,
        login: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 3600
    ) -> Tuple[bool, Optional[str]]:
        """
        Экспорт базы данных в формат .dt
        
        Args:
            base_path: Путь к базе данных (папка)
            output_file: Путь к выходному .dt файлу
            login: Логин пользователя (опционально)
            password: Пароль пользователя (опционально)
            timeout: Таймаут операции в секундах (по умолчанию 1 час)
            
        Returns:
            Кортеж (успех, сообщение_об_ошибке)
            
        Raises:
            OneCError: При критической ошибке выполнения
        """
        # Создаем директорию для выходного файла
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу лога
        log_file = output_file.with_suffix('.log')
        
        # Формируем аргументы командной строки
        args = [
            str(self.exe_path),
            "DESIGNER",
            f'/F"{base_path}"',
            "/DisableStartupMessages",
            f'/DumpIB"{output_file}"',
            f'/Out"{log_file}"'
        ]
        
        # Добавляем авторизацию если указана
        if login:
            args.append(f'/N"{login}"')
        if password:
            args.append(f'/P"{password}"')
            
        logger.info(f"Запуск конфигуратора 1С для экспорта: {base_path}")
        logger.debug(f"Команда (без пароля): {' '.join(args[:6])}")
        
        try:
            # Запускаем процесс
            creationflags = 0
            if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                creationflags = subprocess.CREATE_NO_WINDOW
                
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
            
            # Ожидаем завершения с мониторингом размера файла
            start_time = time.time()
            last_size = 0
            stable_count = 0
            
            while True:
                # Проверяем таймаут
                if time.time() - start_time > timeout:
                    process.kill()
                    error_msg = f"Превышен таймаут экспорта ({timeout} сек)"
                    logger.error(error_msg)
                    return False, error_msg
                    
                # Проверяем завершение процесса
                if process.poll() is not None:
                    break
                    
                # Мониторим размер выходного файла
                if output_file.exists():
                    current_size = output_file.stat().st_size
                    if current_size > 0 and current_size == last_size:
                        stable_count += 1
                    else:
                        stable_count = 0
                    last_size = current_size
                    
                time.sleep(2)
                
            # Получаем код возврата
            return_code = process.returncode
            
            # Проверяем результат
            if return_code != 0:
                error_msg = self._read_error_log(log_file)
                logger.error(f"Конфигуратор завершился с кодом {return_code}")
                return False, error_msg
                
            # Проверяем наличие выходного файла
            if not output_file.exists() or output_file.stat().st_size == 0:
                error_msg = "Выходной файл .dt не создан или пустой"
                logger.error(error_msg)
                return False, error_msg
                
            logger.info(f"Экспорт успешно завершен: {output_file}")
            
            # Удаляем лог если всё успешно
            try:
                if log_file.exists():
                    log_file.unlink()
            except Exception:
                pass
                
            return True, None
            
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = f"Процесс экспорта завис (таймаут {timeout} сек)"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Ошибка при экспорте: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise OneCError(error_msg)
            
    def _read_error_log(self, log_file: Path, max_lines: int = 20) -> str:
        """
        Чтение лога ошибок конфигуратора
        
        Args:
            log_file: Путь к лог-файлу
            max_lines: Максимальное количество строк для чтения
            
        Returns:
            Текст ошибки или сообщение по умолчанию
        """
        if not log_file.exists():
            return "Лог-файл конфигуратора не найден"
            
        try:
            with open(log_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                
            # Берем последние N строк
            error_lines = lines[-max_lines:] if len(lines) > max_lines else lines
            error_text = ''.join(error_lines).strip()
            
            # Ограничиваем длину
            if len(error_text) > 1000:
                error_text = error_text[:1000] + "..."
                
            return error_text if error_text else "Ошибка без описания в логе"
            
        except Exception as e:
            return f"Не удалось прочитать лог: {str(e)}"
            
    @staticmethod
    def find_1cestart() -> Optional[Path]:
        """
        Поиск 1cestart.exe в стандартных местах установки
        
        Returns:
            Путь к 1cestart.exe или None если не найден
        """
        import os
        
        # Возможные пути установки
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        
        search_paths = [
            Path(program_files) / '1cv8' / 'common' / '1cestart.exe',
            Path(program_files_x86) / '1cv8' / 'common' / '1cestart.exe',
        ]
        
        # Поиск всех версий 1С
        for base_path in [Path(program_files) / '1cv8', Path(program_files_x86) / '1cv8']:
            if base_path.exists():
                for version_dir in base_path.iterdir():
                    if version_dir.is_dir():
                        exe_path = version_dir / 'bin' / '1cestart.exe'
                        if exe_path.exists():
                            search_paths.append(exe_path)
        
        # Проверяем каждый путь
        for path in search_paths:
            if path.exists():
                logger.info(f"Найден 1cestart.exe: {path}")
                return path
                
        logger.warning("1cestart.exe не найден в стандартных местах")
        return None
        
    @staticmethod
    def validate_base_path(base_path: Path) -> bool:
        """
        Валидация пути к базе данных
        
        Args:
            base_path: Путь к базе
            
        Returns:
            True если путь валиден
        """
        if not base_path.exists():
            return False
            
        # Для файловой базы проверяем наличие 1Cv8.1CD
        if base_path.is_dir():
            return (base_path / '1Cv8.1CD').exists()
            
        # Для .1CD файла
        if base_path.is_file() and base_path.suffix.lower() == '.1cd':
            return True
            
        return False