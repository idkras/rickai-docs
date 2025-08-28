#!/usr/bin/env python3
"""
Проверка статуса GitHub Pages для Rick.ai документации
"""

import requests
import subprocess
import sys
from pathlib import Path


def run_command(command, capture_output=True):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def check_github_pages():
    """Проверяет доступность GitHub Pages"""
    url = "https://idkras.github.io/rickai-docs/"
    
    print("🔍 Проверяем GitHub Pages...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ GitHub Pages доступен")
            return True
        else:
            print(f"❌ GitHub Pages недоступен (статус: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def check_gh_pages_branch():
    """Проверяет ветку gh-pages"""
    print("\n🌿 Проверяем ветку gh-pages...")
    
    # Проверяем локальную ветку
    result = run_command("git branch -a | grep gh-pages")
    if result.returncode == 0:
        print("✅ Ветка gh-pages существует")
        
        # Проверяем последний коммит
        result = run_command("git log gh-pages -1 --oneline")
        if result.returncode == 0:
            print(f"📝 Последний коммит: {result.stdout.strip()}")
    else:
        print("❌ Ветка gh-pages не найдена")
        return False
    
    return True


def check_mkdocs_config():
    """Проверяет конфигурацию MkDocs"""
    print("\n⚙️ Проверяем конфигурацию MkDocs...")
    
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml не найден")
        return False
    
    print("✅ mkdocs.yml найден")
    
    # Проверяем валидность конфигурации
    result = run_command("mkdocs build --dirty")
    if result.returncode == 0:
        print("✅ Конфигурация MkDocs валидна")
        return True
    else:
        print("❌ Ошибка в конфигурации MkDocs")
        return False


def main():
    """Основная функция"""
    print("🔍 Проверка статуса Rick.ai Documentation")
    print("=" * 50)
    
    # Проверяем, что мы в правильной директории
    if not Path("mkdocs.yml").exists():
        print("❌ mkdocs.yml не найден. Убедитесь, что вы в папке rickai_docs")
        sys.exit(1)
    
    # Выполняем проверки
    config_ok = check_mkdocs_config()
    branch_ok = check_gh_pages_branch()
    pages_ok = check_github_pages()
    
    print("\n" + "=" * 50)
    print("📊 Результаты проверки:")
    print(f"   Конфигурация MkDocs: {'✅' if config_ok else '❌'}")
    print(f"   Ветка gh-pages: {'✅' if branch_ok else '❌'}")
    print(f"   GitHub Pages: {'✅' if pages_ok else '❌'}")
    
    if all([config_ok, branch_ok, pages_ok]):
        print("\n🎉 Все проверки пройдены!")
        print("📖 Документация доступна: https://idkras.github.io/rickai-docs/")
    else:
        print("\n⚠️  Есть проблемы. Проверьте настройки.")
        if not pages_ok:
            print("💡 GitHub Pages может обновляться с задержкой (до 10 минут)")


if __name__ == "__main__":
    main()
