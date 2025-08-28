#!/bin/bash

# Скрипт для деплоя документации Rick.ai на GitHub Pages

echo "🚀 Начинаем деплой документации Rick.ai..."

# Проверяем, что мы в правильной директории
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Ошибка: mkdocs.yml не найден. Убедитесь, что вы находитесь в корне проекта."
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt

# Собираем документацию
echo "🔨 Собираем документацию..."
mkdocs build

# Проверяем, что сборка прошла успешно
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке документации"
    exit 1
fi

# Добавляем все изменения в git
echo "📝 Добавляем изменения в git..."
git add .

# Проверяем, есть ли изменения для коммита
if git diff --cached --quiet; then
    echo "ℹ️  Нет изменений для коммита"
else
    # Коммитим изменения
    echo "💾 Коммитим изменения..."
    git commit -m "Update documentation $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Отправляем изменения в репозиторий
echo "📤 Отправляем изменения в репозиторий..."
git push origin main

# Деплоим на GitHub Pages
echo "🌐 Деплоим на GitHub Pages..."
mkdocs gh-deploy --force

echo "✅ Деплой завершен! Документация доступна по адресу:"
echo "   https://idkras.github.io/rickai-docs/"
