# VipAvenue Adjust AppMetrica Integration

## Обзор

Интеграция VipAvenue с Adjust и AppMetrica для отслеживания мобильных событий и конверсий.

## Настройка

### 1. Adjust Configuration

```javascript
// Инициализация Adjust
AdjustConfig config = new AdjustConfig(this, appToken, environment);
Adjust.onCreate(config);
```

### 2. AppMetrica Configuration

```javascript
// Инициализация AppMetrica
AppMetrica.activate(this, new AppMetricaConfig(apiKey));
```

## События

### Основные события

- `purchase` - покупка
- `registration` - регистрация
- `login` - вход в систему
- `view_item` - просмотр товара

### Пример отправки события

```javascript
// Adjust
AdjustEvent event = new AdjustEvent(eventToken);
event.addRevenue(price, currency);
Adjust.trackEvent(event);

// AppMetrica
AppMetrica.reportEvent("purchase", {
    "price": price,
    "currency": currency,
    "product_id": productId
});
```

## Отладка

### Проверка событий

1. Включите debug режим
2. Проверьте логи в консоли
3. Убедитесь в правильности токенов

### Логирование

```javascript
// Adjust debug
AdjustConfig config = new AdjustConfig(this, appToken, AdjustConfig.ENVIRONMENT_SANDBOX);
config.setLogLevel(LogLevel.VERBOSE);

// AppMetrica debug
AppMetricaConfig config = new AppMetricaConfig(apiKey);
config.setLogEnabled(true);
```

## Мониторинг

### Метрики для отслеживания

- **Conversion Rate** - конверсия
- **Revenue** - доход
- **User Acquisition** - привлечение пользователей
- **Retention** - удержание

### Дашборды

- Adjust Dashboard: https://app.adjust.com
- AppMetrica Dashboard: https://appmetrica.yandex.ru

## Troubleshooting

### Частые проблемы

1. **События не отправляются**
   - Проверьте интернет соединение
   - Убедитесь в правильности токенов
   - Проверьте настройки privacy

2. **Неправильные данные**
   - Проверьте формат событий
   - Убедитесь в корректности параметров
   - Проверьте кодировку

3. **Задержки в данных**
   - Нормальная задержка: 1-2 часа
   - Для real-time данных используйте API

## API Reference

### Adjust API

```javascript
// Track custom event
AdjustEvent event = new AdjustEvent(eventToken);
event.addCallbackParameter("key", "value");
event.addPartnerParameter("partner_key", "partner_value");
Adjust.trackEvent(event);
```

### AppMetrica API

```javascript
// Send custom event
AppMetrica.reportEvent("custom_event", {
    "parameter1": "value1",
    "parameter2": "value2"
});
```

## Поддержка

При возникновении проблем:

1. Проверьте документацию
2. Обратитесь в техподдержку
3. Создайте тикет с логами

---

*Документация обновлена: 28 августа 2025*
