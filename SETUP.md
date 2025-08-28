# Настройка Rick.ai Documentation

## 🎯 Что было сделано

1. **Очищен репозиторий** - удалены все старые файлы
2. **Настроен MkDocs** - создана чистая конфигурация для документации
3. **Настроен GitHub Actions** - автоматический деплой на GitHub Pages
4. **Создан скрипт деплоя** - удобный способ обновления документации

## 📁 Структура проекта

```
rickai_docs/
├── .github/workflows/deploy.yml  # GitHub Actions для автоматического деплоя
├── docs/                         # Исходные markdown файлы
│   ├── index.md                  # Главная страница
│   ├── vipavenue.adjust_appmetrica.md  # Документация по VipAvenue
│   └── stylesheets/              # Дополнительные стили
├── mkdocs.yml                    # Конфигурация MkDocs
├── requirements.txt              # Python зависимости
├── deploy.sh                     # Скрипт для деплоя
├── README.md                     # Описание проекта
└── .gitignore                    # Исключения для git
```

## 🚀 Как использовать

### Локальная разработка

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустите локальный сервер:**
   ```bash
   mkdocs serve
   ```

3. **Откройте браузер:**
   ```
   http://127.0.0.1:8000
   ```

### Деплой на GitHub Pages

#### Автоматический (рекомендуется)
Просто отправьте изменения в репозиторий:
```bash
git add .
git commit -m "Update documentation"
git push origin main
```

GitHub Actions автоматически соберет и задеплоит документацию.

#### Ручной деплой
Используйте скрипт:
```bash
./deploy.sh
```

Или команду MkDocs:
```bash
mkdocs gh-deploy
```

## ⚙️ Настройки GitHub Pages

1. **Перейдите в настройки репозитория** на GitHub
2. **Включите GitHub Pages** в разделе "Pages"
3. **Выберите источник:** "GitHub Actions"
4. **Документация будет доступна по адресу:**
   ```
   https://idkras.github.io/rickai-docs/
   ```

## 📝 Добавление новой документации

1. **Создайте markdown файл** в папке `docs/`
2. **Добавьте страницу в навигацию** в `mkdocs.yml`:
   ```yaml
   nav:
     - Home: index.md
     - Новая страница: new-page.md
   ```
3. **Задеплойте изменения**

## 🔧 Конфигурация MkDocs

Основные настройки в `mkdocs.yml`:
- **Тема:** Material for MkDocs
- **Поиск:** Включен с подсветкой
- **Навигация:** Секции, вкладки, кнопка "Наверх"
- **Код:** Подсветка синтаксиса, копирование
- **Дополнительные возможности:** Mermaid диаграммы, вкладки, детали

## 🛠️ Полезные команды

```bash
# Сборка документации
mkdocs build

# Локальный сервер разработки
mkdocs serve

# Деплой на GitHub Pages
mkdocs gh-deploy

# Проверка конфигурации
mkdocs serve --strict
```

## 📞 Поддержка

- **Telegram:** @rick_ai
- **GitHub Issues:** Создать issue в репозитории
