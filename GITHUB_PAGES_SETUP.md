# ⚙️ Настройка GitHub Pages для Rick.ai Documentation

## 🎯 Цель

Настроить GitHub Pages для отображения статических HTML/CSS файлов без использования GitHub Actions.

## 📋 Пошаговая настройка

### 1. Перейдите в настройки репозитория

1. Откройте репозиторий: https://github.com/idkras/rickai-docs
2. Перейдите в **Settings** (вкладка вверху)
3. В левом меню найдите **Pages**

### 2. Настройте источник

В разделе **Pages**:

1. **Source**: Выберите `Deploy from a branch`
2. **Branch**: Выберите `gh-pages`
3. **Folder**: Оставьте `/(root)` (по умолчанию)
4. Нажмите **Save**

### 3. Проверьте настройки

После сохранения вы увидите:
- ✅ **Your site is published at https://idkras.github.io/rickai-docs/**
- 🟡 **GitHub Pages is currently building your site**

## 🔄 Workflow

### Локальная сборка
```bash
# Сборка документации
mkdocs build

# Или через Makefile
make build
```

### Деплой статики
```bash
# Быстрый деплой
python quick_deploy.py

# Или через Makefile
make quick-deploy
```

### Проверка статуса
```bash
# Проверить статус GitHub Pages
python check_pages.py

# Или через Makefile
make check-pages
```

## 📁 Структура веток

- **`main`** - исходный код и конфигурация MkDocs
- **`gh-pages`** - статические HTML/CSS файлы (автоматически создается)

## ⚠️ Важные моменты

1. **Нет GitHub Actions** - сборка происходит только локально
2. **Статические файлы** - GitHub Pages показывает только готовые HTML/CSS
3. **Ветка gh-pages** - создается автоматически командой `mkdocs gh-deploy`
4. **Задержка обновления** - GitHub Pages может обновляться с задержкой до 10 минут

## 🆘 Устранение проблем

### GitHub Pages возвращает 404

1. Проверьте настройки в **Settings** → **Pages**
2. Убедитесь, что выбрана ветка `gh-pages`
3. Подождите 5-10 минут после деплоя
4. Запустите `python check_pages.py`

### Ветка gh-pages не существует

1. Выполните деплой: `python quick_deploy.py`
2. Ветка создастся автоматически

### Ошибки сборки

1. Проверьте конфигурацию: `mkdocs build`
2. Установите зависимости: `pip install -r requirements.txt`
3. Проверьте файл `mkdocs.yml`

## 📖 Полезные команды

```bash
# Полная проверка
make check-pages

# Локальный просмотр
make serve

# Быстрый деплой
make quick-deploy

# Полный деплой с установкой зависимостей
make deploy
```
