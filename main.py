#!/usr/bin/env python3
"""
CLI инструмент для преобразования учебного конфигурационного языка в TOML.
"""
import sys
import argparse
from config_parser import Lexer, Parser
from toml_converter import convert_to_toml


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="Конвертер учебного конфигурационного языка в TOML"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Путь к выходному TOML файлу"
    )
    
    args = parser.parse_args()
    
    # Читаем из stdin
    try:
        input_text = sys.stdin.read()
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Лексический анализ
    try:
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"Lexical error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Синтаксический анализ
    try:
        parser = Parser(tokens)
        ast = parser.parse()
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Конвертация в TOML
    try:
        toml_output = convert_to_toml(ast)
    except Exception as e:
        print(f"Conversion error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Запись в файл
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(toml_output)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Successfully converted to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

