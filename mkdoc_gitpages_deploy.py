#!/usr/bin/env python3
"""
Быстрый деплой документации Rick.ai
Упрощенная версия для случаев, когда зависимости уже установлены
"""

import subprocess
import sys
import os
import shutil
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


def copy_symlinks_to_real_files():
    """Копирует символические ссылки в реальные файлы для сборки"""
    print("🔗 Копируем символические ссылки в реальные файлы...")
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ Папка docs не найдена")
        return False
    
    copied_files = []
    
    # Ищем все символические ссылки в папке docs
    for file_path in docs_dir.rglob("*"):
        if file_path.is_symlink():
            try:
                # Получаем путь, на который указывает символическая ссылка
                target_path = file_path.resolve()
                
                # Проверяем, что целевой файл существует
                if target_path.exists():
                    # Создаем временную копию
                    temp_path = file_path.with_suffix(file_path.suffix + ".temp")
                    
                    # Копируем содержимое целевого файла
                    shutil.copy2(target_path, temp_path)
                    
                    # Удаляем символическую ссылку
                    file_path.unlink()
                    
                    # Переименовываем временный файл
                    temp_path.rename(file_path)
                    
                    copied_files.append(str(file_path))
                    print(f"✅ Скопирован: {file_path.name}")
                else:
                    print(f"⚠️  Целевой файл не найден: {target_path}")
                    # Создаем файл с базовым содержимым
                    create_fallback_file(file_path)
                    copied_files.append(str(file_path))
                    print(f"✅ Создан fallback файл: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ Ошибка при копировании {file_path}: {e}")
                return False
    
    if copied_files:
        print(f"📋 Обработано файлов: {len(copied_files)}")
    else:
        print("ℹ️  Символические ссылки не найдены")
    
    return True


def create_fallback_file(file_path):
    """Создает файл с базовым содержимым если целевой файл недоступен"""
    fallback_content = f"""# {file_path.stem.replace('-', ' ').title()}

## Обзор

Документация по {file_path.stem.replace('-', ' ').lower()}.

## Примечание

Этот файл был создан автоматически при деплое, так как исходный файл недоступен.

---

*Документация обновлена: {datetime.now().strftime('%d %B %Y')}*
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fallback_content)


def main():
    """Быстрый деплой"""
    print("🚀 Быстрый деплой документации Rick.ai")
    print("=" * 40)
    
    # Проверяем, что мы в правильной директории
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml не найден")
        sys.exit(1)
    
    # Копируем символические ссылки в реальные файлы
    if not copy_symlinks_to_real_files():
        print("❌ Ошибка при копировании символических ссылок")
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
