# 🚀 Быстрый старт Rick.ai Documentation

## ⚡ Одна команда для деплоя

```bash
python quick_deploy.py
```

Эта команда автоматически:
- ✅ Соберет документацию
- ✅ Сделает коммит изменений
- ✅ Отправит в репозиторий
- ✅ Задеплоит на GitHub Pages

## 🛠️ Альтернативные способы

### Makefile (рекомендуется)
```bash
make help          # Показать все команды
make quick-deploy  # Быстрый деплой
make deploy        # Полный деплой с установкой зависимостей
make serve         # Локальный сервер для разработки
```

### Bash скрипт
```bash
./deploy.sh
```

### Ручные команды
```bash
mkdocs build
git add . && git commit -m "Update" && git push
mkdocs gh-deploy
```

## 📖 Результат

Документация будет доступна по адресу:
**https://idkras.github.io/rickai-docs/**

## 🔧 Первоначальная настройка

Если вы впервые запускаете проект:

```bash
make setup
```

Это установит зависимости и соберет документацию.

## 📝 Добавление новой документации

1. Создайте markdown файл в `docs/`
2. Добавьте в навигацию в `mkdocs.yml`
3. Запустите `python quick_deploy.py`

## 🆘 Если что-то не работает

1. Проверьте, что вы в папке `rickai_docs/`
2. Убедитесь, что git настроен: `git status`
3. Проверьте зависимости: `pip install -r requirements.txt`
4. Запустите полный деплой: `python deploy_docs.py`
