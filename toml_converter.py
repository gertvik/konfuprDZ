"""
Конвертер AST в TOML формат.
"""
import tomlkit
from typing import Any, Dict, List


def to_toml(value: Any) -> Any:
    """
    Конвертировать значение в TOML формат.
    
    Args:
        value: Значение для конвертации
        
    Returns:
        Значение в формате TOML
    """
    if isinstance(value, dict):
        return {k: to_toml(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_toml(item) for item in value]
    elif isinstance(value, (int, float, str, bool)):
        return value
    else:
        return str(value)


def convert_to_toml(data: Any) -> str:
    """
    Конвертировать данные в строку TOML.
    
    Args:
        data: Данные для конвертации
        
    Returns:
        Строка в формате TOML
    """
    if isinstance(data, dict):
        doc = tomlkit.document()
        for key, value in data.items():
            doc[key] = to_toml(value)
        return tomlkit.dumps(doc)
    elif isinstance(data, list):
        # Если корневой элемент - массив
        doc = tomlkit.document()
        doc["array"] = to_toml(data)
        return tomlkit.dumps(doc)
    else:
        # Примитивное значение
        doc = tomlkit.document()
        doc["value"] = to_toml(data)
        return tomlkit.dumps(doc)

