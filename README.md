# Rick.ai Documentation

Документация Rick.ai - AI-ассистированные проекты и интеграции.

## 🚀 Быстрый старт

1. Установите зависимости:
```bash
pip install mkdocs-material
```

2. Запустите локальный сервер:
```bash
mkdocs serve
```

3. Откройте http://127.0.0.1:8000

## ⚙️ Настройка GitHub Pages

Для правильной работы GitHub Pages без Actions:
- 📖 [Подробная инструкция](GITHUB_PAGES_SETUP.md)
- 🚀 [Быстрый старт](QUICK_START.md)

## 📚 Документация

- **Сайт**: https://idkras.github.io/rickai-docs/
- **GitHub**: https://github.com/idkras/rickai-docs

## 📞 Поддержка

- **Telegram**: @rick_ai
- **GitHub Issues**: Создать issue

## 🛠️ Разработка

### Автоматические скрипты

**Полный деплой (рекомендуется):**
```bash
python deploy_docs.py
```

**Быстрый деплой (если зависимости уже установлены):**
```bash
python quick_deploy.py
```

**Использование Makefile:**
```bash
make help          # Показать все команды
make install       # Установить зависимости
make build         # Собрать документацию
make serve         # Запустить локальный сервер
make deploy        # Полный деплой
make quick-deploy  # Быстрый деплой
```

### Ручные команды

Для сборки документации:
```bash
mkdocs build
```

Для деплоя на GitHub Pages:
```bash
mkdocs gh-deploy
```
