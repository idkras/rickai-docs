#!/usr/bin/env python3
"""
Быстрый деплой документации Rick.ai
Упрощенная версия для случаев, когда зависимости уже установлены
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(command, check=True):
    """Выполняет команду"""
    try:
        subprocess.run(command, shell=True, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Быстрый деплой"""
    print("🚀 Быстрый деплой документации Rick.ai")
    print("=" * 40)
    
    # Проверяем, что мы в правильной директории
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml не найден")
        sys.exit(1)
    
    # Собираем документацию
    print("📦 Собираем документацию...")
    if not run_command("mkdocs build"):
        sys.exit(1)
    
    # Git операции
    print("📝 Git операции...")
    run_command("git add .")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_command(f'git commit -m "Quick update {timestamp}"')
    run_command("git push origin main")
    
    # Деплой
    print("🌐 Деплоим на GitHub Pages...")
    if not run_command("mkdocs gh-deploy --force"):
        sys.exit(1)
    
    print("✅ Деплой завершен!")
    print("📖 https://idkras.github.io/rickai-docs/")


if __name__ == "__main__":
    main()
