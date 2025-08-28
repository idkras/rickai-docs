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
    symlink_info = []  # Сохраняем информацию о символических ссылках
    
    # Ищем все символические ссылки в папке docs
    for file_path in docs_dir.rglob("*"):
        if file_path.is_symlink():
            try:
                # Сохраняем информацию о символической ссылке
                target_path = file_path.resolve()
                symlink_info.append({
                    'file_path': file_path,
                    'target_path': target_path
                })
                
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
                    print(f"❌ Целевой файл не найден: {target_path}")
                    print(f"❌ Символическая ссылка {file_path} указывает на несуществующий файл")
                    return False
                    
            except Exception as e:
                print(f"❌ Ошибка при копировании {file_path}: {e}")
                return False
    
    # Сохраняем информацию о символических ссылках для восстановления
    if symlink_info:
        save_symlink_info(symlink_info)
    
    if copied_files:
        print(f"📋 Обработано файлов: {len(copied_files)}")
    else:
        print("ℹ️  Символические ссылки не найдены")
    
    return True


def save_symlink_info(symlink_info):
    """Сохраняет информацию о символических ссылках"""
    info_file = Path(".symlink_info")
    with open(info_file, 'w') as f:
        for info in symlink_info:
            f.write(f"{info['file_path']}|{info['target_path']}\n")


def restore_symlinks():
    """Восстанавливает символические ссылки после деплоя"""
    print("🔗 Восстанавливаем символические ссылки...")
    
    info_file = Path(".symlink_info")
    if not info_file.exists():
        print("ℹ️  Информация о символических ссылках не найдена")
        return
    
    restored_count = 0
    
    with open(info_file, 'r') as f:
        for line in f:
            try:
                file_path_str, target_path_str = line.strip().split('|')
                file_path = Path(file_path_str)
                target_path = Path(target_path_str)
                
                # Удаляем текущий файл
                if file_path.exists():
                    file_path.unlink()
                
                # Создаем символическую ссылку
                file_path.symlink_to(target_path)
                restored_count += 1
                print(f"✅ Восстановлена ссылка: {file_path.name}")
                
            except Exception as e:
                print(f"❌ Ошибка при восстановлении {file_path_str}: {e}")
    
    # Удаляем временный файл
    info_file.unlink()
    
    if restored_count > 0:
        print(f"📋 Восстановлено ссылок: {restored_count}")





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
    
    # Восстанавливаем символические ссылки
    restore_symlinks()
    
    print("✅ Деплой завершен!")
    print("📖 https://idkras.github.io/rickai-docs/")


if __name__ == "__main__":
    main()
