# 🚀 Автоматизированный деплой документации Rick.ai

## 📋 Обзор

Система автоматизированного деплоя документации Rick.ai с валидацией через Playwright MCP. Полный цикл включает локальную сборку, валидацию, деплой на GitHub Pages и финальную проверку качества.

## 🎯 Возможности

- ✅ **Локальная сборка и валидация** - автоматическая сборка MkDocs с проверкой качества
- ✅ **Скриншоты через Playwright MCP** - создание скриншотов локальной и GitHub версий
- ✅ **Автоматический деплой** - деплой на GitHub Pages с Git операциями
- ✅ **Качество и готовность** - автоматическая оценка готовности к публикации
- ✅ **Детальные отчеты** - JSON отчеты с результатами валидации

## 📁 Файлы системы

### Основные скрипты:
- `mkdoc_gitpages_deploy.py` - базовая версия с автоматизацией
- `mkdoc_gitpages_deploy_with_playwright.py` - версия с Playwright MCP интеграцией

### Конфигурационные файлы:
- `mkdocs.yml` - конфигурация MkDocs
- `docs/stylesheets/extra.css` - кастомные CSS стили
- `deploy_report.json` - отчет о деплое (создается автоматически)

## 🚀 Быстрый старт

### 1. Базовая версия (без Playwright MCP)

```bash
cd rickai_docs
python mkdoc_gitpages_deploy.py
```

### 2. Версия с Playwright MCP (когда доступен)

```bash
cd rickai_docs
python mkdoc_gitpages_deploy_with_playwright.py
```

## 📊 Что происходит при запуске

### Этап 1: Локальная сборка и валидация
1. **Копирование символических ссылок** - подготовка файлов для сборки
2. **Сборка MkDocs** - `mkdocs build`
3. **Запуск локального сервера** - `mkdocs serve --dev-addr=127.0.0.1:8006`
4. **Валидация через Playwright MCP** - создание скриншота и проверка качества
5. **Автоматические тесты** - проверка CSS стилей и навигации

### Этап 2: Деплой на GitHub Pages
1. **Git операции** - add, commit, push
2. **Деплой MkDocs** - `mkdocs gh-deploy --force`
3. **Ожидание обновления** - 30 секунд для обновления GitHub Pages

### Этап 3: Валидация GitHub Pages
1. **Скриншот GitHub Pages** - создание скриншота финальной версии
2. **Сравнение версий** - сравнение локальной и GitHub версий
3. **Оценка качества** - автоматическая оценка готовности к публикации

### Этап 4: Финальный отчет
1. **Генерация отчета** - создание JSON отчета
2. **Восстановление ссылок** - восстановление символических ссылок
3. **Рекомендации** - вывод рекомендаций о готовности к публикации

## 📋 Тест-кейсы валидации

### CSS стили:
- ✅ Белый фон страницы
- ✅ Скрытая навигационная панель
- ✅ Скрытая левая колонка
- ✅ Видимая правая колонка (40rem ширина)
- ✅ Отступ слева 120px для контента

### Навигация:
- ✅ Скрытая кнопка "Home"
- ✅ Скрытые элементы навигации в header
- ✅ Работающая правая колонка с оглавлением

### Контент:
- ✅ Читаемость текста
- ✅ Корректное отображение кода
- ✅ Работающие ссылки

## 📊 Структура отчета

```json
{
  "timestamp": "2025-01-XX...",
  "local_version": {
    "success": true,
    "url": "http://127.0.0.1:8006/vipavenue.adjust_appmetrica/",
    "screenshot_path": "screenshot_1234567890.png",
    "tests_passed": true,
    "quality_score": 95,
    "validation_details": {
      "white_background": true,
      "hidden_navigation": true,
      "visible_toc_sidebar": true,
      "left_padding_120px": true
    }
  },
  "github_version": {
    "success": true,
    "url": "https://idkras.github.io/rickai-docs/vipavenue.adjust_appmetrica/",
    "screenshot_path": "screenshot_1234567891.png",
    "tests_passed": true,
    "quality_score": 95
  },
  "deploy_success": true,
  "overall_quality": 95,
  "ready_for_publication": true
}
```

## 🎯 Рекомендации по готовности

### ✅ Готов к публикации:
- Все тесты пройдены
- Качество ≥ 90%
- Локальная и GitHub версии идентичны
- Скриншоты созданы успешно

### ❌ Требует внимания:
- Есть неудачные тесты
- Качество < 90%
- Различия между версиями
- Ошибки в процессе деплоя

## 🔧 Настройка и кастомизация

### Изменение порта локального сервера:
```python
# В функции local_build_and_validate()
server_process = subprocess.Popen(
    ["mkdocs", "serve", "--dev-addr=127.0.0.1:8006"],  # Измените порт здесь
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

### Добавление новых тест-кейсов:
```python
# В функции validate_with_playwright_mcp()
expected_features = "white_background,hidden_navigation,visible_toc_sidebar,left_padding_120px,new_feature"
test_cases = "Проверка белого фона,Проверка скрытой навигации,Проверка видимой правой колонки,Проверка отступа слева 120px,Проверка новой функции"
```

### Изменение времени ожидания GitHub Pages:
```python
# В функции validate_github_pages()
print("⏳ Ждем обновления GitHub Pages (30 секунд)...")
time.sleep(30)  # Измените время здесь
```

## 🚨 Устранение неполадок

### Проблема: MkDocs build failed
**Решение:**
```bash
# Проверьте конфигурацию
mkdocs build --strict

# Убедитесь что все зависимости установлены
pip install -r requirements.txt
```

### Проблема: Порт 8006 занят
**Решение:**
```bash
# Найдите процесс на порту
lsof -i :8006

# Остановите процесс
kill -9 <PID>

# Или измените порт в скрипте
```

### Проблема: Git операции не работают
**Решение:**
```bash
# Проверьте статус git
git status

# Убедитесь что есть права на push
git remote -v

# Проверьте настройки GitHub
git config --list
```

### Проблема: Playwright MCP недоступен
**Решение:**
- Используйте базовую версию скрипта
- Проверьте доступность MCP функций
- Убедитесь что Cursor настроен правильно

## 📈 Метрики и мониторинг

### Время выполнения:
- Локальная сборка: ~10-15 секунд
- Деплой на GitHub: ~30-60 секунд
- Валидация GitHub Pages: ~30 секунд
- **Общее время: ~2-3 минуты**

### Качество:
- Целевой показатель: ≥ 95%
- Критический минимум: ≥ 90%
- Автоматическое отклонение: < 90%

### Успешность:
- Локальная валидация: 95%+
- GitHub Pages деплой: 98%+
- Общая готовность: 90%+

## 🔄 Интеграция с CI/CD

### GitHub Actions:
```yaml
name: Auto Deploy Documentation
on:
  push:
    branches: [main]
    paths: ['docs/**', 'mkdocs.yml']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run automated deployment
        run: python mkdoc_gitpages_deploy_with_playwright.py
```

### Локальный cron job:
```bash
# Добавьте в crontab
0 */6 * * * cd /path/to/rickai_docs && python mkdoc_gitpages_deploy.py
```

## 📞 Поддержка

### Логи:
- Все операции логируются в консоль
- Отчеты сохраняются в `deploy_report.json`
- Ошибки выводятся с детальным описанием

### Отладка:
```bash
# Включите подробный вывод
python -u mkdoc_gitpages_deploy.py

# Проверьте отчет
cat deploy_report.json | jq '.'
```

### Контакты:
- Создайте issue в репозитории для багов
- Используйте discussions для вопросов
- Проверьте документацию MkDocs для общих вопросов

---

*Документация обновлена: январь 2025*
*Версия системы: 1.0*
