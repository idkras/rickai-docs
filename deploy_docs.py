#!/usr/bin/env python3
"""
Автоматический деплой документации Rick.ai на GitHub Pages
Выполняет все необходимые действия: установка зависимостей, сборка, коммит, пуш, деплой
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path


class Colors:
    """Цвета для вывода в терминал"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_step(message, color=Colors.OKBLUE):
    """Выводит сообщение о текущем шаге"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")


def print_success(message):
    """Выводит сообщение об успехе"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message):
    """Выводит сообщение об ошибке"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message):
    """Выводит предупреждение"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def run_command(command, check=True, capture_output=False, cwd=None):
    """Выполняет команду и возвращает результат"""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True,
                cwd=cwd
            )
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check,
                cwd=cwd
            )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Команда '{command}' завершилась с ошибкой: {e}")
            sys.exit(1)
        return e


def check_prerequisites():
    """Проверяет необходимые условия для деплоя"""
    print_step("Проверяем необходимые условия...")
    
    # Проверяем, что мы в правильной директории
    if not Path("mkdocs.yml").exists():
        print_error("mkdocs.yml не найден. Убедитесь, что вы находитесь в корне проекта rickai_docs")
        sys.exit(1)
    
    # Проверяем, что git инициализирован
    if not Path(".git").exists():
        print_error("Git репозиторий не инициализирован")
        sys.exit(1)
    
    # Проверяем, что есть remote origin
    result = run_command("git remote get-url origin", check=False, capture_output=True)
    if result.returncode != 0:
        print_error("Remote origin не настроен")
        sys.exit(1)
    
    print_success("Все необходимые условия выполнены")


def install_dependencies():
    """Устанавливает Python зависимости"""
    print_step("Устанавливаем Python зависимости...")
    
    # Проверяем, есть ли requirements.txt
    if not Path("requirements.txt").exists():
        print_warning("requirements.txt не найден, пропускаем установку зависимостей")
        return
    
    # Устанавливаем зависимости
    run_command("pip install -r requirements.txt")
    print_success("Зависимости установлены")


def build_documentation():
    """Собирает документацию"""
    print_step("Собираем документацию...")
    
    # Очищаем предыдущую сборку
    if Path("site").exists():
        run_command("rm -rf site")
    
    # Собираем документацию
    run_command("mkdocs build")
    
    # Проверяем, что сборка прошла успешно
    if not Path("site").exists():
        print_error("Сборка документации не удалась")
        sys.exit(1)
    
    print_success("Документация собрана успешно")


def git_operations():
    """Выполняет git операции"""
    print_step("Выполняем git операции...")
    
    # Проверяем статус git
    status_result = run_command("git status --porcelain", capture_output=True)
    has_changes = bool(status_result.stdout.strip())
    
    if not has_changes:
        print_warning("Нет изменений для коммита")
        return False
    
    # Добавляем все изменения
    run_command("git add .")
    
    # Создаем коммит
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Update documentation {timestamp}"
    run_command(f'git commit -m "{commit_message}"')
    
    # Отправляем изменения
    run_command("git push origin main")
    
    print_success("Git операции выполнены")
    return True


def deploy_to_github_pages():
    """Деплоит документацию на GitHub Pages"""
    print_step("Деплоим на GitHub Pages...")
    
    # Деплоим с помощью mkdocs
    run_command("mkdocs gh-deploy --force")
    
    print_success("Деплой на GitHub Pages завершен")


def show_final_info():
    """Показывает финальную информацию"""
    print_step("Деплой завершен!", Colors.HEADER)
    print(f"{Colors.BOLD}Документация доступна по адресу:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}https://idkras.github.io/rickai-docs/{Colors.ENDC}")
    print()
    print(f"{Colors.BOLD}Полезные команды:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}mkdocs serve{Colors.ENDC} - запуск локального сервера")
    print(f"{Colors.OKCYAN}mkdocs build{Colors.ENDC} - сборка документации")
    print(f"{Colors.OKCYAN}mkdocs gh-deploy{Colors.ENDC} - деплой на GitHub Pages")


def main():
    """Главная функция"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🚀 Автоматический деплой документации Rick.ai")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    try:
        # Проверяем условия
        check_prerequisites()
        
        # Устанавливаем зависимости
        install_dependencies()
        
        # Собираем документацию
        build_documentation()
        
        # Выполняем git операции
        git_operations()
        
        # Деплоим на GitHub Pages
        deploy_to_github_pages()
        
        # Показываем финальную информацию
        show_final_info()
        
    except KeyboardInterrupt:
        print_error("Деплой прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
