# Инструкция: Интеграция Adjust с AppMetrica для UTM-трекинга
*Глубокий анализ для мобильной атрибуции и кросс-платформенного трекинга инструкция обновлена в августе 2025 года.*

---

## 📋 Next Actions

### 🔧 Технические задачи
- [x] Для всех параметров дописать комментарий, что это за поле adjust
- [x] Flutter: сделать адаптацию кода
- [ ] Обновить текст запросов разрешений:
  - [ ] Локация: сразу же спрашиваем...
  - [ ] Разрешение на трекинг...
  - [ ] Разрешение на уведомления...
- [x] Добавить события в AppMetrica на согласие/несогласие:
  - [ ] Локация
  - [ ] Уведомления  
  - [ ] Разрешение на трекинг

### 📱 Пользовательский опыт
- [ ] Предложить обновление текста для запроса доступа к локации:
  > "Для предоставления персонализированных предложений и скидок на основе вашего местоположения, приложение использует данные о вашем местоположении. Эти данные не будут переданы третьим лицам без вашего согласия."

### 🔗 Deep Links
- [ ] Проверить, что в AppMetrica отправляются диплинки:
  `deep_link_path=/catalog/womens/clothes/dresses/seven-lab-cotton-dress`
- [ ] Отправлять событие что пользователь пришел с диплинком
- [ ] Отправлять событие что пользователь действительно попал на страницу с диплинком и замерять, на какую страницу пришел в итоге

### 📚 Разметить события и описать логику трекинга для 
- [ ] Расписать для ASO
- [ ] Расписать пример для мотивированного трафика
- [ ] Расписать пример для email
- [ ] расприать пример для перехода с website vipavenue.ru

</details>

<details open>
<summary><strong>## 🚀 QUICK START · 5 минут для разработчика - готовый код</strong></summary>

<details open>
<summary><strong>Flutter (main.dart)</strong></summary>

- Прочитайте официальную adjust flutter документацию: <a href="https://dev.adjust.com/en/sdk/flutter">https://dev.adjust.com/en/sdk/flutter</a> 
- Посмотрите на примеры кода в гитхабе: <a href="https://github.com/adjust/flutter_sdk/tree/master/example">https://github.com/adjust/flutter_sdk/tree/master/example</a>


```dart
Add the following to your pubspec.yaml file:
dependencies:
   adjust_sdk: ^5.4.2

Navigate to your project and run the following command. Visual Studio automatically runs this command after you edit the pubspec.yaml file.
$ flutter packages get

———

import 'package:flutter/material.dart';
import 'package:adjust_sdk/adjust_sdk.dart';
import 'package:appmetrica_plugin/appmetrica_plugin.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VipAvenue',
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  void initState() {
    super.initState();
    _initializeSDKs();
  }

  // ✅ ИНИЦИАЛИЗАЦИЯ: AppMetrica и Adjust в Flutter
  Future<void> _initializeSDKs() async {
    try {
      // 1. AppMetrica (первым!) - инициализируем первой для корректной работы
      const String appMetricaKey = 'YOUR_APPMETRICA_API_KEY'; // TODO: заменить на реальный API ключ из AppMetrica Dashboard (https://appmetrica.yandex.ru)
      
      // ✅ ПРАВИЛЬНАЯ КОНФИГУРАЦИЯ AppMetrica
      final appMetricaConfig = AppMetricaConfig(appMetricaKey)
        ..withLocationTracking(true) // Разрешаем сбор данных о местоположении
        ..withHandleFirstActivationAsUpdate(false); // Первый запуск = новый установ
      
      // ✅ ПРАВИЛЬНАЯ АКТИВАЦИЯ (без await - синхронная операция)
      AppMetrica.activate(appMetricaConfig);
      print('✅ AppMetrica активирована');
      
      // 2. Adjust (вторым!) - инициализируем после AppMetrica
      const String adjustToken = 'YOUR_ADJUST_APP_TOKEN'; // TODO: заменить на реальный App Token из Adjust Dashboard (https://app.adjust.com)
      
      // Создаем конфигурацию Adjust для продакшена
      final adjustConfig = AdjustConfig(adjustToken, AdjustEnvironment.production);
      
      // ✅ ПРАВИЛЬНЫЙ CALLBACK: Adjust → AppMetrica
      adjustConfig.setAttributionChangedCallback((AdjustAttribution attribution) {
        _handleAttribution(attribution); // Обрабатываем полученную атрибуцию
      });
      
      // Запускаем Adjust
      Adjust.start(adjustConfig);
      print('✅ Adjust активирован');
      
      // 3. Синхронизация идентификаторов
      Future.delayed(Duration(seconds: 2), () {
        _syncDeviceIdentifiers();
      });
      
    } catch (e) {
      print('❌ Ошибка инициализации SDK: $e');
    }
  }

  // ✅ ОБРАБОТКА: Attribution данных
  void _handleAttribution(AdjustAttribution attribution) {
    try {
      final params = {
        // 🎯 Adjust параметры для аналитики - данные от системы атрибуции
        'adjust_tracker': attribution.trackerName ?? 'unknown',
        'adjust_network': attribution.network ?? 'unknown',
        'adjust_campaign': attribution.campaign ?? 'unknown',
        'adjust_creative': attribution.creative ?? 'unknown',
        'adjust_click_label': attribution.clickLabel ?? 'unknown',
        'adjust_adid': Adjust.getAdid() ?? 'unknown',
        'is_first_launch': attribution.isFirstLaunch ?? false,
        
        // 🔗 UTM параметры для корректной атрибуции
        'utm_source': attribution.network ?? 'unknown',
        'utm_campaign': attribution.campaign ?? 'unknown',
        'utm_content': attribution.creative ?? '',
        'utm_medium': '', // Восстанавливается в Rick.ai по правилам
        
        // ⏰ Дополнительные параметры для аналитики
        'attribution_timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000,
        'attribution_type': attribution.isFirstLaunch == true ? 'install' : 'reinstall'
      };
      
      // ✅ Отправляем в AppMetrica с adjust_adid в каждом событии
      final adjustAdid = Adjust.getAdid();
      final paramsWithAdjustID = Map<String, dynamic>.from(params);
      paramsWithAdjustID['adjust_adid'] = adjustAdid ?? 'unknown';
      AppMetrica.reportEvent('adjust attributed utm params', paramsWithAdjustID);
      
      // ✅ ОБМЕН ИДЕНТИФИКАТОРАМИ: Записываем adjust_adid в AppMetrica
      final adjustAdid = Adjust.getAdid();
      if (adjustAdid != null) {
        // ⚠️ ВАЖНО: setUserProfileID НЕ добавляет adjust_adid в каждое событие!
        // Он только связывает все события пользователя с этим ID в AppMetrica
        AppMetrica.setUserProfileID(adjustAdid);
        print('✅ Adjust ADID записан в AppMetrica: $adjustAdid');
        
        // ✅ ДОПОЛНИТЕЛЬНО: Отправляем событие с adjust_adid для аналитики
        AppMetrica.reportEvent('adjust_id_synced', {
          'adjust_adid': adjustAdid,
          'appmetrica_device_id': AppMetrica.getDeviceID() ?? 'unknown',
          'sync_timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000
        });
      }
      
      // ✅ ПРАВИЛЬНЫЙ ОБМЕН ИДЕНТИФИКАТОРАМИ: Записываем appmetrica_device_id в Adjust
      final appMetricaDeviceId = AppMetrica.getDeviceID(); // Синхронный вызов
      if (appMetricaDeviceId != null) {
        final adjustEvent = AdjustEvent('YOUR_DEVICE_ID_SYNC_TOKEN');
        adjustEvent.addCallbackParameter('appmetrica_device_id', appMetricaDeviceId);
        adjustEvent.addCallbackParameter('sync_timestamp', (DateTime.now().millisecondsSinceEpoch ~/ 1000).toString());
        Adjust.trackEvent(adjustEvent);
        print('✅ AppMetrica Device ID записан в Adjust: $appMetricaDeviceId');
      }
      
      // Логирование в flow.rick.ai
      _logToRickAI(attribution, params);
      
    } catch (e) {
      print('❌ Ошибка обработки attribution: $e');
    }
  }

  // ✅ ОБМЕН ИДЕНТИФИКАТОРАМИ: Синхронизация device ID между платформами
  Future<void> _syncDeviceIdentifiers() async {
    try {
      // Синхронизируем Adjust ADID в AppMetrica
      final adjustAdid = Adjust.getAdid();
      if (adjustAdid != null) {
        AppMetrica.setUserProfileID(adjustAdid);
        print('✅ Adjust ADID синхронизирован в AppMetrica: $adjustAdid');
      }
      
      // ✅ ПРАВИЛЬНАЯ СИНХРОНИЗАЦИЯ AppMetrica Device ID в Adjust
      final appMetricaDeviceId = AppMetrica.getDeviceID(); // Синхронный вызов
      if (appMetricaDeviceId != null) {
        final adjustEvent = AdjustEvent('YOUR_DEVICE_ID_SYNC_TOKEN'); // TODO: создать специальный Event Token в Adjust Dashboard для синхронизации device ID
        adjustEvent.addCallbackParameter('appmetrica_device_id', appMetricaDeviceId);
        adjustEvent.addCallbackParameter('adjust_adid', Adjust.getAdid() ?? 'unknown');
        adjustEvent.addCallbackParameter('sync_type', 'appmetrica_to_adjust');
        adjustEvent.addCallbackParameter('sync_timestamp', (DateTime.now().millisecondsSinceEpoch ~/ 1000).toString());
        Adjust.trackEvent(adjustEvent);
        print('✅ AppMetrica Device ID синхронизирован в Adjust: $appMetricaDeviceId');
      }
      
    } catch (e) {
      print('❌ Ошибка синхронизации идентификаторов: $e');
    }
  }

  // ✅ ЛОГИРОВАНИЕ: В flow.rick.ai
  Future<void> _logToRickAI(AdjustAttribution attribution, Map<String, dynamic> params) async {
    try {
      final appMetricaDeviceId = AppMetrica.getDeviceID(); // Синхронный вызов
      
      final logData = {
        'event_type': 'attribution_data',
        'timestamp': DateTime.now().toIso8601String(),
        'app_info': {
          'app_id': 'com.vipavenue.app',
          'platform': 'flutter',
          'version': '1.0.0',
          'build': '1'
        },
        'device_info': {
          'device_id': Adjust.getAdid() ?? 'unknown',
          'appmetrica_device_id': appMetricaDeviceId ?? 'unknown',
          'platform': 'flutter'
        },
        'attribution_data': {
          'adjust_network': attribution.network ?? 'unknown',
          'adjust_campaign': attribution.campaign ?? 'unknown',
          'adjust_creative': attribution.creative ?? 'unknown',
          'adjust_tracker': attribution.trackerName ?? 'unknown',
          'adjust_click_label': attribution.clickLabel ?? 'unknown',
          'is_first_launch': attribution.isFirstLaunch ?? false,
          'attribution_type': attribution.isFirstLaunch == true ? 'install' : 'reinstall'
        },
        'utm_data': {
          'utm_source': attribution.network ?? 'unknown',
          'utm_medium': '', // Восстанавливается в Rick.ai по правилам
          'utm_campaign': attribution.campaign ?? 'unknown',
          'utm_content': attribution.creative ?? ''
        },
        'sdk_status': {
          'adjust_initialized': true,
          'appmetrica_initialized': true,
          'attribution_received': true,
          'event_sent_to_appmetrica': true
        },
        'error_info': {
          'has_errors': false,
          'error_messages': []
        }
      };
      
      // Отправка в flow.rick.ai
      await _sendToRickAI(logData);
      
    } catch (e) {
      print('❌ Ошибка логирования в Rick.ai: $e');
    }
  }

  // 🌐 ОТПРАВКА: В flow.rick.ai
  Future<void> _sendToRickAI(Map<String, dynamic> data) async {
    try {
      final url = Uri.parse('https://flow.rick.ai/webhook/ff27caff-574f-4183-a29b-c2cac4147d43');
      
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(data),
      );
      
      if (response.statusCode != 200) {
        print('❌ Rick.ai вернул статус: ${response.statusCode}');
      } else {
        print('✅ Данные отправлены в Rick.ai');
      }
      
    } catch (e) {
      print('❌ Ошибка отправки в Rick.ai: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('VipAvenue')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('SDK инициализированы'),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // ✅ Тестовое событие с adjust_adid
                final adjustAdid = Adjust.getAdid();
                AppMetrica.reportEvent('test_event', {
                  'test_param': 'test_value',
                  'adjust_adid': adjustAdid ?? 'unknown',
                  'timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000
                });
                print('✅ Тестовое событие с adjust_adid отправлено');
              },
              child: Text('Отправить тестовое событие'),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // ✅ Пример покупки с adjust_adid
                final adjustAdid = Adjust.getAdid();
                AppMetrica.reportEvent('purchase', {
                  'amount': 1000.0,
                  'currency': 'RUB',
                  'product_id': 'test_product',
                  'adjust_adid': adjustAdid ?? 'unknown',
                  'timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000
                });
                print('✅ Событие покупки с adjust_adid отправлено');
              },
              child: Text('Отправить событие покупки'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### **Конфигурация Flutter:**

#### **pubspec.yaml:**
```yaml
dependencies:
  flutter:
    sdk: flutter
  adjust_sdk: ^5.4.2  # ✅ ПРАВИЛЬНАЯ ВЕРСИЯ (официальная документация)
  appmetrica_plugin: ^2.0.0
  http: ^1.1.0
```

#### **Android: android/app/src/main/AndroidManifest.xml**
```xml
<manifest>
    <application>
        <!-- AppMetrica -->
        <meta-data
            android:name="com.yandex.metrica.ApiKey"
            android:value="YOUR_APPMETRICA_API_KEY" />
            
        <!-- Adjust -->
        <meta-data
            android:name="com.adjust.sdk.AppToken"
            android:value="YOUR_ADJUST_APP_TOKEN" />
    </application>
</manifest>
```

#### **iOS: ios/Runner/Info.plist**
```xml
<dict>
    <!-- AppMetrica -->
    <key>APPMETRICA_API_KEY</key>
    <string>YOUR_APPMETRICA_API_KEY</string>
    
    <!-- Adjust -->
    <key>ADJUST_APP_TOKEN</key>
    <string>YOUR_ADJUST_APP_TOKEN</string>
    
    <!-- App Tracking Transparency -->
    <key>NSUserTrackingUsageDescription</key>
    <string>Мы используем данные для персонализации вашего опыта и показа подходящих вам товаров.</string>
</dict>
```

</details>

### **📋 ЧЕКЛИСТ ДЛЯ КОМАНДЫ РАЗРАБОТКИ**

#### **🔧 Техническая проверка:**
- [ ] **SDK инициализация**: AppMetrica инициализируется ПЕРВОЙ, затем Adjust
- [ ] **API ключи**: Добавлены в Info.plist/strings.xml/AndroidManifest.xml
- [ ] **Версия SDK**: `adjust_sdk: ^5.4.2` в pubspec.yaml
- [ ] **Callback**: `setAttributionChangedCallback` настроен правильно
- [ ] **Device ID**: Синхронизация между Adjust и AppMetrica работает

#### **📊 События, которые должны отправляться в AppMetrica:**

**1. Основные события атрибуции:**
- [ ] `adjust attributed utm params` - с полными UTM параметрами и `adjust_adid`
- [ ] `adjust_id_synced` - подтверждение синхронизации ID
- [ ] `device_id_sync` - синхронизация при запуске

**2. События App Tracking Transparency (iOS):**
- [ ] `tracking_authorized` - пользователь разрешил трекинг
- [ ] `tracking_denied` - пользователь отказал в трекинге
- [ ] `tracking_restricted` - трекинг ограничен системой

**3. События Deep Links:**
- [ ] `deep_link_opened` - открытие через deep link
- [ ] `deep_link_deferred` - отложенный deep link
- [ ] `universal_link` - универсальная ссылка

**4. События покупок:**
- [ ] `purchase` - покупка товара с `adjust_adid`
- [ ] `purchase_with_utm` - покупка с UTM параметрами

**5. События пользовательского опыта:**
- [ ] `location_permission_granted` - разрешение на локацию
- [ ] `location_permission_denied` - отказ в локации
- [ ] `notification_permission_granted` - разрешение на уведомления
- [ ] `notification_permission_denied` - отказ в уведомлениях

#### **🎯 Проверка в AppMetrica Dashboard:**
- [ ] Все события содержат параметр `adjust_adid`
- [ ] UTM параметры корректно передаются
- [ ] Связь между Adjust и AppMetrica работает
- [ ] Нет ошибок в логах приложения

#### **📱 Тестирование на устройствах:**
- [ ] iOS 14.5+ - ATT диалог появляется
- [ ] Android - Google Play Services работают
- [ ] Deep links открывают правильные страницы
- [ ] Покупки трекаются корректно

<details>
<summary><strong>iOS (AppDelegate.swift)</strong></summary>

        appMetricaConfig.locationTracking = true // AI todo: допиши зачем и как правильно 
        задает, привести пример. Правильно обработать в листалке...
        appMetricaConfig.handleFirstActivationAsUpdate = false // AI todo: допиши зачем и как правильно


```swift
import AdjustSdk
import AppMetricaCore
import AppTrackingTransparency
import os.log

class AppDelegate: UIResponder, UIApplicationDelegate {
    private let logger = Logger(subsystem: "com.vipavenue.app", category: "SDK")
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // 1. AppMetrica (первым!)
        guard let appMetricaKey = Bundle.main.object(forInfoDictionaryKey: "APPMETRICA_API_KEY") as? String,
              !appMetricaKey.isEmpty else {
            logger.error("APPMETRICA_API_KEY не найден в Info.plist")
            return true
        }
        
        let appMetricaConfig = AppMetricaConfiguration(apiKey: appMetricaKey)!
        
        // ✅ КОНФИГУРАЦИЯ: Настройки AppMetrica через UserDefaults
        let userDefaults = UserDefaults.standard
        
        // 📍 locationTracking - разрешает AppMetrica собирать данные о местоположении пользователя
        let locationTracking = userDefaults.bool(forKey: "appmetrica_location_tracking")
        
        // 🔄 handleFirstActivationAsUpdate - как обрабатывать первый запуск приложения
        // true = считать первый запуск как обновление (для статистики)
        // false = считать как новый установ (правильно для аналитики установок)
        let handleFirstActivationAsUpdate = userDefaults.bool(forKey: "appmetrica_handle_first_activation_as_update")
        
        appMetricaConfig.locationTracking = locationTracking
        appMetricaConfig.handleFirstActivationAsUpdate = handleFirstActivationAsUpdate
        
        // Логируем настройки
        logger.info("AppMetrica config: locationTracking=\(locationTracking), handleFirstActivationAsUpdate=\(handleFirstActivationAsUpdate)") 
        AppMetrica.activate(with: appMetricaConfig)
        
        // 2. Adjust (вторым!)
        guard let adjustToken = Bundle.main.object(forInfoDictionaryKey: "ADJUST_APP_TOKEN") as? String,
              !adjustToken.isEmpty else {
            logger.error("ADJUST_APP_TOKEN не найден в Info.plist")
            return true
        }
        
        let adjustConfig = ADJConfig(appToken: adjustToken, environment: ADJEnvironmentProduction)
        
        // Callback: Adjust → AppMetrica
        adjustConfig?.setAttributionChangedBlock { attribution in
            if let attribution = attribution {
                // Проверяем что AppMetrica готова
                if AppMetrica.isActivated {
                    let params = [
                        // 🎯 Adjust параметры для аналитики - данные от системы атрибуции
                        
                        // 📊 adjust_tracker - уникальный идентификатор трекера в Adjust
                        // Трекер = ссылка в Adjust, которая отслеживает откуда пришел пользователь
                        // Пример: "abc123" - это ID конкретной рекламной ссылки
                        "adjust_tracker": attribution.trackerName ?? "unknown",
                        
                        // 🌐 adjust_network - источник трафика (рекламная сеть)
                        // Примеры: "facebook", "google", "yandex", "organic" (органический трафик)
                        // Показывает где была размещена реклама
                        "adjust_network": attribution.network ?? "unknown",
                        
                        // 📢 adjust_campaign - название рекламной кампании
                        // Пример: "summer2025_dresses", "black_friday_2025"
                        // Помогает понять какая кампания привела пользователя
                        "adjust_campaign": attribution.campaign ?? "unknown",
                        
                        // 🎨 adjust_creative - креатив/баннер рекламы
                        // Пример: "video_banner", "story_ad", "carousel_ad"
                        // Показывает какой именно рекламный материал сработал
                        "adjust_creative": attribution.creative ?? "unknown",
                        
                        // 🏷️ adjust_click_label - дополнительная метка клика
                        // Используется для детализации: "premium_dresses", "discount_30%"
                        // Помогает понять на что именно кликнул пользователь
                        "adjust_click_label": attribution.clickLabel ?? "unknown",
                        
                        // 📱 adjust_adid - уникальный идентификатор устройства в Adjust
                        // Постоянный ID устройства, не меняется при переустановке приложения
                        // Используется для связывания данных между сессиями
                        "adjust_adid": Adjust.adid() ?? "unknown",
                        
                        // 🆕 is_first_launch - первый ли это запуск приложения
                        // true = пользователь установил приложение впервые
                        // false = пользователь уже запускал приложение раньше
                        "is_first_launch": attribution.isFirstLaunch ?? false,
                        
                        // 🔗 UTM параметры для корректной атрибуции - стандарт веб-аналитики
                        
                        // 📍 utm_source - источник трафика (тот же что и adjust_network)
                        // Используется для совместимости с веб-аналитикой
                        "utm_source": attribution.network ?? "unknown",
                        
                        // 📢 utm_campaign - название кампании (тот же что и adjust_campaign)
                        // Стандартный параметр для всех аналитических систем
                        "utm_campaign": attribution.campaign ?? "unknown",
                        
                        // 🎨 utm_content - контент рекламы (тот же что и adjust_creative)
                        "utm_content": attribution.creative ?? "",
                        
                        // 📊 utm_medium - канал рекламы (пустой, восстанавливается в Rick.ai)
                        // Примеры: "cpc", "banner", "video", "social"
                        // Восстанавливается автоматически по правилам Rick.ai
                        "utm_medium": "",
                        
                        // ⏰ Дополнительные параметры для аналитики
                        
                        // 🕐 attribution_timestamp - время получения атрибуции
                        // Unix timestamp (секунды с 1970 года)
                        // Нужен для анализа времени между кликом и установкой
                        "attribution_timestamp": Date().timeIntervalSince1970,
                        
                        // 📈 attribution_type - тип атрибуции
                        // "install" = новый пользователь установил приложение
                        // "reinstall" = существующий пользователь переустановил приложение
                        "attribution_type": attribution.isFirstLaunch == true ? "install" : "reinstall"
                    ]
                    
                    // ✅ Отправляем событие в AppMetrica с adjust_adid
                    let adjustAdid = Adjust.adid()
                    var paramsWithAdjustID = params
                    paramsWithAdjustID["adjust_adid"] = adjustAdid ?? "unknown"
                    AppMetrica.reportEvent("adjust attributed utm params", parameters: paramsWithAdjustID)
                    
                    // 🔄 ОБМЕН ИДЕНТИФИКАТОРАМИ: Записываем adjust_adid в AppMetrica
                    // Это позволяет связывать данные между Adjust и AppMetrica
                    if let adjustAdid = Adjust.adid() {
                        // setUserProfileID - устанавливает постоянный ID пользователя в AppMetrica
                        // ⚠️ ВАЖНО: adjust_adid НЕ добавляется в каждое событие!
                        // Вместо этого AppMetrica автоматически связывает ВСЕ события пользователя с этим ID
                        // Это более эффективно чем добавлять adjust_adid в каждое событие
                        AppMetrica.setUserProfileID(adjustAdid)
                        logger.info("Adjust ADID записан в AppMetrica: \(adjustAdid)")
                        
                        // 📊 Отправляем специальное событие с adjust_adid для аналитики
                        // Это событие поможет отследить связь между Adjust и AppMetrica
                        AppMetrica.reportEvent("adjust_id_synced", parameters: [
                            "adjust_adid": adjustAdid,
                            "appmetrica_device_id": AppMetrica.deviceID() ?? "unknown",
                            "sync_timestamp": Date().timeIntervalSince1970
                        ])
                    }
                    
                    // 🔄 ОБМЕН ИДЕНТИФИКАТОРАМИ: Записываем appmetrica_device_id в Adjust
                    // Это позволяет Adjust знать ID устройства из AppMetrica для связывания данных
                    if let appMetricaDeviceId = AppMetrica.deviceID() {
                        // Создаем специальное событие в Adjust для синхронизации ID
                        let adjustEvent = ADJEvent(eventToken: "YOUR_DEVICE_ID_SYNC_TOKEN")
                        
                        // addCallbackParameter - добавляет параметр к событию
                        // ⚠️ ВАЖНО: appmetrica_device_id добавляется ТОЛЬКО в это специальное событие
                        // Adjust НЕ будет автоматически добавлять его во все события
                        // Это отличается от AppMetrica.setUserProfileID()
                        adjustEvent?.addCallbackParameter("appmetrica_device_id", value: appMetricaDeviceId)
                        adjustEvent?.addCallbackParameter("sync_timestamp", value: String(Date().timeIntervalSince1970))
                        
                        // trackEvent - отправляет событие в Adjust
                        Adjust.trackEvent(adjustEvent)
                        logger.info("AppMetrica Device ID записан в Adjust: \(appMetricaDeviceId)")
                    }
                    
                    // Логирование в flow.rick.ai
                    self.logToRickAI(attribution: attribution, params: params)
                } else {
                    self.logger.error("AppMetrica не активирована при получении attribution")
                }
            }
        }
        
        Adjust.appDidLaunch(adjustConfig)
        
        // ✅ ОБМЕН ИДЕНТИФИКАТОРАМИ: Синхронизация при запуске приложения
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            self.syncDeviceIdentifiers()
        }

        // 🔒 3. Запрашиваем разрешение на трекинг (iOS 14.5+)
        // App Tracking Transparency (ATT) - система Apple для защиты конфиденциальности
        // Пользователь должен дать разрешение на использование IDFA (рекламный идентификатор)
        // Если не дают разрешение, то Adjust работает без IDFA (ограниченная атрибуция)
        
        // asyncAfter - выполняем код через 1 секунду после запуска
        // Это требование Apple - нельзя запрашивать разрешение сразу при запуске
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.requestTrackingAuthorization()
        }
        
        return true
    }
    
    // MARK: - App Tracking Transparency (ATT)
    // 🔒 Система Apple для защиты конфиденциальности пользователей
    
    private func requestTrackingAuthorization() {
        // #available(iOS 14.5, *) - проверяем доступность ATT (только с iOS 14.5)
        if #available(iOS 14.5, *) {
            // requestTrackingAuthorization - запрашиваем разрешение на трекинг
            // Показывает пользователю диалог с объяснением зачем нужны данные
            ATTrackingManager.requestTrackingAuthorization { status in
                // Обработка результата должна быть на главном потоке (UI)
                DispatchQueue.main.async {
                    self.handleTrackingAuthorizationStatus(status)
                }
            }
        }
    }
    
    private func handleTrackingAuthorizationStatus(_ status: ATTrackingManager.AuthorizationStatus) {
        // Обрабатываем результат запроса разрешения на трекинг
        switch status {
        case .authorized:
            // ✅ Пользователь разрешил трекинг - получаем IDFA
            logger.info("Пользователь разрешил трекинг - получаем IDFA")
            
            // IDFA (Identifier for Advertisers) - уникальный рекламный идентификатор
            // Доступен для Adjust и AppMetrica для точной атрибуции
            let idfa = ASIdentifierManager.shared().advertisingIdentifier.uuidString
            logger.info("IDFA получен: \(idfa)")
            
        case .denied:
            // ❌ Пользователь отказал в трекинге - используем ограниченную аналитику
            logger.warning("Пользователь отказал в трекинге - используем ограниченную аналитику")
            
            // ✅ Отправляем событие об отказе с adjust_adid
            let adjustAdid = Adjust.adid()
            AppMetrica.reportEvent("tracking_denied", parameters: [
                "timestamp": Date().timeIntervalSince1970,
                "platform": "ios",
                "adjust_adid": adjustAdid ?? "unknown"
            ])
            
        case .restricted:
            logger.warning("Трекинг ограничен системой - используем ограниченную аналитику")
            // ✅ Отправляем событие с adjust_adid
            let adjustAdid = Adjust.adid()
            AppMetrica.reportEvent("tracking_restricted", parameters: [
                "timestamp": Date().timeIntervalSince1970,
                "platform": "ios",
                "adjust_adid": adjustAdid ?? "unknown"
            ])
            
        case .notDetermined:
            logger.info("Статус трекинга не определен")
            
        @unknown default:
            logger.warning("Неизвестный статус трекинга: \(status.rawValue)")
        }
    }
    
    // TODO создать вебхук на сервере, который логирует все данные, например, в redis или PostgreSQL для аналитики
    // Логирование в flow.rick.ai
    private func logToRickAI(attribution: ADJAttribution, params: [String: Any]) {
        let logData: [String: Any] = [
            "event_type": "attribution_data",
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "app_info": [
                "app_id": Bundle.main.bundleIdentifier ?? "unknown",
                "platform": "ios",
                "version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown",
                "build": Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "unknown"
            ],
            "device_info": [
                "device_id": Adjust.adid() ?? "unknown", // TODO: перепроверить код - убедиться что Adjust.adid() возвращает корректный ID устройства
                "appmetrica_device_id": AppMetrica.deviceID() ?? "unknown",
                "idfa": ASIdentifierManager.shared().advertisingIdentifier.uuidString,
                "idfv": UIDevice.current.identifierForVendor?.uuidString ?? "unknown",
                "os_version": UIDevice.current.systemVersion,
                "device_model": UIDevice.current.model
            ],
            "attribution_data": [
                "adjust_network": attribution.network ?? "unknown",
                "adjust_campaign": attribution.campaign ?? "unknown",
                "adjust_creative": attribution.creative ?? "unknown",
                "adjust_tracker": attribution.trackerName ?? "unknown",
                "adjust_click_label": attribution.clickLabel ?? "unknown",
                "is_first_launch": attribution.isFirstLaunch ?? false,
                "attribution_type": attribution.isFirstLaunch == true ? "install" : "reinstall"
            ],
            "utm_data": [
                "utm_source": attribution.network ?? "unknown",
                "utm_medium": "" // Восстанавливается в Rick.ai по правилам        
                "utm_campaign": attribution.campaign ?? "unknown",
                "utm_content": attribution.creative ?? ""
            ],
            "sdk_status": [
                "adjust_initialized": true,
                "appmetrica_initialized": AppMetrica.isActivated,
                "attribution_received": true,
                "event_sent_to_appmetrica": true
            ],
            "error_info": [
                "has_errors": false,
                "error_messages": []
            ]
        ]
        
        // Отправка в flow.rick.ai
        sendToRickAI(data: logData)
    }
    
    private func sendToRickAI(data: [String: Any]) {
        guard let url = URL(string: "https://flow.rick.ai/webhook/ff27caff-574f-4183-a29b-c2cac4147d43") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: data)
        } catch {
            logger.error("Ошибка сериализации данных для Rick.ai: \(error)")
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                self.logger.error("Ошибка отправки в Rick.ai: \(error)")
            } else if let httpResponse = response as? HTTPURLResponse {
                if httpResponse.statusCode != 200 {
                    self.logger.error("Rick.ai вернул статус: \(httpResponse.statusCode)")
                }
            }
        }.resume()
    }
}
```
</details>
<details>
<summary><strong>Android (MainApplication.kt)</strong></summary>


- везде flatter

```kotlin
import com.adjust.sdk.Adjust
import com.adjust.sdk.AdjustConfig
import com.adjust.sdk.AdjustAttribution
import com.yandex.metrica.AppMetrica
import com.yandex.metrica.AppMetricaConfig
import android.util.Log

class MainApplication : Application() {
    companion object {
        private const val TAG = "MainApplication"
    }
    
    override fun onCreate() {
        super.onCreate()
        
        // 1. AppMetrica (первым!)
        val appMetricaKey = getString(R.string.appmetrica_api_key)
        if (appMetricaKey.isEmpty()) {
            Log.e(TAG, "APPMETRICA_API_KEY не найден в strings.xml")
            return
        }
        
        val appMetricaConfig = AppMetricaConfig.newConfigBuilder(appMetricaKey)
            .withLocationTracking(true)
            .handleFirstActivationAsUpdate(false)
            .build()
        
        AppMetrica.activate(this, appMetricaConfig)
        
        // 2. Adjust (вторым!)
        val adjustToken = getString(R.string.adjust_app_token)
        if (adjustToken.isEmpty()) {
            Log.e(TAG, "ADJUST_APP_TOKEN не найден в strings.xml")
            return
        }
        
        val adjustConfig = AdjustConfig(this, adjustToken, AdjustConfig.ENVIRONMENT_PRODUCTION)
        
        // Callback: Adjust → AppMetrica
        adjustConfig.setOnAttributionChangedListener { attribution ->
            attribution?.let {
                if (AppMetrica.isActivated) {
                    val params = mapOf(
                        // Adjust параметры для аналитики
                        "adjust_tracker" to (it.trackerName ?: "unknown"),
                        "adjust_network" to (it.network ?: "unknown"),
                        "adjust_campaign" to (it.campaign ?: "unknown"),
                        "adjust_creative" to (it.creative ?: "unknown"),
                        "adjust_click_label" to (it.clickLabel ?: "unknown"),
                        "adjust_adid" to (Adjust.getAdid() ?: "unknown"),
                        "is_first_launch" to (it.isFirstLaunch ?: false),
                        
                        // UTM параметры для корректной атрибуции
                        "utm_source" to (it.network ?: "unknown"),
                        "utm_campaign" to (it.campaign ?: "unknown"),
                        "utm_content" to (it.creative ?: ""),
                        "utm_medium" to "" // Восстанавливается в Rick.ai по правилам
                        
                        // Дополнительные параметры для аналитики
                        "attribution_timestamp" to System.currentTimeMillis() / 1000,
                        "attribution_type" to (if (it.isFirstLaunch == true) "install" else "reinstall")
                    )
                    
                    AppMetrica.reportEvent("adjust attributed utm params", params)
                    
                    // Логирование в flow.rick.ai
                    logToRickAI(it, params)
                } else {
                    Log.e(TAG, "AppMetrica не активирована при получении attribution")
                }
            }
        }
        
        Adjust.onCreate(adjustConfig)
    }
    
    // Логирование в flow.rick.ai
    private fun logToRickAI(attribution: AdjustAttribution, params: Map<String, Any>) {
        val logData = mapOf(
            "event_type" to "attribution_data",
            "timestamp" to java.time.Instant.now().toString(),
            "app_info" to mapOf(
                "app_id" to (packageName),
                "platform" to "android",
                "version" to (try { packageManager.getPackageInfo(packageName, 0).versionName } catch (e: Exception) { "unknown" }),
                "build" to (try { packageManager.getPackageInfo(packageName, 0).versionCode.toString() } catch (e: Exception) { "unknown" })
            ),
            "device_info" to mapOf(
                "device_id" to (Adjust.getAdid() ?: "unknown"),
                "appmetrica_device_id" to (AppMetrica.getDeviceID() ?: "unknown"),
                "android_id" to (Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID) ?: "unknown"),
                "os_version" to Build.VERSION.RELEASE,
                "device_model" to Build.MODEL
            ),
            "attribution_data" to mapOf(
                "adjust_network" to (attribution.network ?: "unknown"), // ✅ Adjust Network - источник трафика (facebook, google, organic)
                "adjust_tracker" to (attribution.trackerName ?: "unknown"), // ✅ Adjust Tracker - уникальный идентификатор трекера
                "adjust_campaign" to (attribution.campaign ?: "unknown"), // ✅ Adjust Campaign - название рекламной кампании
                "adjust_creative" to (attribution.creative ?: "unknown"), // ✅ Adjust Creative - креатив/баннер рекламы
                "adjust_click_label" to (attribution.clickLabel ?: "unknown"), // ✅ Adjust Click Label - метка клика для детализации
                "is_first_launch" to (attribution.isFirstLaunch ?: false), // ✅ Is First Launch - первый запуск приложения
                "attribution_type" to (if (attribution.isFirstLaunch == true) "install" else "reinstall") // ✅ Attribution Type - тип атрибуции
            ),
            "utm_data" to mapOf(
                "utm_source" to (attribution.network ?: "unknown"),
                "utm_campaign" to (attribution.campaign ?: "unknown"),
                "utm_content" to (attribution.creative ?: ""),
                "utm_medium" to "" // Восстанавливается в Rick.ai по правилам
            ),
            "sdk_status" to mapOf(
                "adjust_initialized" to true,
                "appmetrica_initialized" to AppMetrica.isActivated,
                "attribution_received" to true,
                "event_sent_to_appmetrica" to true
            ),
            "error_info" to mapOf(
                "has_errors" to false,
                "error_messages" to emptyList<String>()
            )
        )
        
        // Отправка в flow.rick.ai
        sendToRickAI(logData)
    }
    
    private fun sendToRickAI(data: Map<String, Any>) {
        val url = URL("https://flow.rick.ai/webhook/ff27caff-574f-4183-a29b-c2cac4147d43")
        
        Thread {
            try {
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true
                
                val jsonData = org.json.JSONObject(data)
                val outputStream = connection.outputStream
                outputStream.write(jsonData.toString().toByteArray())
                outputStream.flush()
                outputStream.close()
                
                val responseCode = connection.responseCode
                if (responseCode != 200) {
                    Log.e(TAG, "Rick.ai вернул статус: $responseCode")
                }
                
                connection.disconnect()
            } catch (e: Exception) {
                Log.e(TAG, "Ошибка отправки в Rick.ai: ${e.message}")
            }
        }.start()
    }
}
```
</details>

### **Конфигурация API ключей:**

#### **iOS: Info.plist**
```xml
<!-- Добавьте в Info.plist -->
<key>APPMETRICA_API_KEY</key>
<string>YOUR_APPMETRICA_API_KEY_HERE</string>
<key>ADJUST_APP_TOKEN</key>
<string>YOUR_ADJUST_APP_TOKEN_HERE</string>
```

#### **Android: strings.xml**
```xml
<!-- Добавьте в res/values/strings.xml -->
<resources>
    <string name="appmetrica_api_key">YOUR_APPMETRICA_API_KEY_HERE</string>
    <string name="adjust_app_token">YOUR_ADJUST_APP_TOKEN_HERE</string>
</resources>
```

### **Чек-лист из 5 пунктов:**
1. ✅ Добавьте API ключи в Info.plist/strings.xml
2. ✅ Замените `YOUR_*_KEY` на реальные ключи
3. ✅ Добавьте код в AppDelegate/MainApplication
4. ✅ Проверьте что AppMetrica инициализируется первой
5. ✅ Запустите приложение и проверьте логи

### **Тест "работает/не работает":**
- ✅ **Работает**: В AppMetrica dashboard видите событие `adjust_attribution` с полными параметрами
- ❌ **Не работает**: В логах ошибки "API_KEY не найден" или событие отсутствует в AppMetrica

### **Параметры для проверки в AppMetrica:**
- `adjust_network` - источник трафика (yandex direct, google ads, aso organic)
- `adjust_campaign` - название кампании
- `adjust_adid` - уникальный adjust device ID устройства
- `is_first_launch` - true для новых пользователей
- `attribution_type` - "install" или "reinstall"
- `utm_source` - источник для UTM аналитики

</details>

---

<details open>
<summary><strong>## 🔐 iOS App Tracking Transparency (ATT) - Обязательно!</strong></summary>

### **1.1 Что нужно для iOS ATTrackingManager:**

#### **Обязательные требования:**
- **iOS 14.5+**: ATTrackingManager доступен только с iOS 14.5
- **Info.plist**: Добавить описание использования данных
- **Timing**: Запрашивать разрешение не раньше чем через 1 секунду после запуска
- **Fallback**: Обрабатывать все статусы разрешения

#### **Что получаем при согласии:**
- **IDFA** (Identifier for Advertisers) - уникальный идентификатор
- **Полная атрибуция** - Adjust получает IDFA и точнее определяет какой пользователь перешел.

#### **Что получаем при отказе:**
- **Ограниченная атрибуция** - только через SKAdNetwork
- **Нет IDFA** - используем другие идентификаторы
- **Базовая аналитика** - основные события работают

### **1.2 Экран согласия пользователя - что написать:**

#### **✅ ПРАВИЛЬНЫЙ ТЕКСТ (высокий конверсия):**
```
🎯 Персонализированный опыт

Мы используем данные для:
• Показывать релевантные товары и предложения
• Анализировать эффективность рекламных кампаний
• Улучшать работу приложения

Ваши данные:
• Не передаются третьим лицам
• Используются только для улучшения сервиса
• Хранятся в соответствии с GDPR

Разрешить персонализацию?
```

#### **❌ НЕПРАВИЛЬНЫЙ ТЕКСТ (низкая конверсия):**
```
Мы собираем ваши данные для рекламы
Разрешить трекинг?
```
### **1.3 Настройка Info.plist:**

```xml
<!-- Добавьте в Info.plist -->
<key>NSUserTrackingUsageDescription</key>
<string>Мы используем данные для персонализации вашего опыта и показа подходящих вам товаров. Ваши данные не передаются третьим лицам и используются только для улучшения сервиса VipAvenue.</string>

<key>SKAdNetworkItems</key>
<array>
    <dict>
        <key>SKAdNetworkIdentifier</key>
        <string>v79kvwwj4g.skadnetwork</string>
    </dict>
    <dict>
        <key>SKAdNetworkIdentifier</key>
        <string>22mmun2rn5.skadnetwork</string>
    </dict>
    <!-- Добавьте все нужные SKAdNetwork идентификаторы -->
</array>
```

### **1.4 Обработка всех статусов:**

```swift
// В AppDelegate добавьте:
private func handleTrackingAuthorizationStatus(_ status: ATTrackingManager.AuthorizationStatus) {
    switch status {
    case .authorized:
        // ✅ Пользователь согласился - полная аналитика
        logger.info("Трекинг разрешен - используем IDFA")
        let idfa = ASIdentifierManager.shared().advertisingIdentifier.uuidString
        
        // Отправляем событие о согласии
        AppMetrica.reportEvent("tracking_authorized", parameters: [
            "idfa": idfa,
            "timestamp": Date().timeIntervalSince1970
        ])
        
    case .denied:
        // ❌ Пользователь отказал - ограниченная аналитика
        logger.warning("Трекинг отклонен - используем SKAdNetwork")
        AppMetrica.reportEvent("tracking_denied", parameters: [
            "timestamp": Date().timeIntervalSince1970,
            "reason": "user_denied"
        ])
        
    case .restricted:
        // ⚠️ Система ограничила - ограниченная аналитика
        logger.warning("Трекинг ограничен системой")
        AppMetrica.reportEvent("tracking_restricted", parameters: [
            "timestamp": Date().timeIntervalSince1970,
            "reason": "system_restricted"
        ])
        
    case .notDetermined:
        // 🔄 Статус не определен
        logger.info("Статус трекинга не определен")
        
    @unknown default:
        logger.warning("Неизвестный статус трекинга")
    }
}
```

### **1.5 Чек-лист для ATT:**
1. ✅ Добавлен `NSUserTrackingUsageDescription` в Info.plist
2. ✅ Добавлены `SKAdNetworkItems` для fallback
3. ✅ Запрос разрешения через 1+ секунду после запуска
4. ✅ Обработка всех статусов разрешения
5. ✅ Логирование событий согласия/отказа
6. ✅ Тестирование на реальном устройстве iOS 14.5+
7. ✅ Проверка что App Store не отклоняет приложение

</details>

---

<details open>
<summary><strong>🔄 СХЕМА РАБОТЫ ADJUST И APPMETRICA</strong></summary>


### **Как работает интеграция по коду:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Реклама с     │───▶│  Adjust Tracker │───▶│   Adjust SDK    │
│      UTM        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────┬───────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Analytics      │◀───│  AppMetrica SDK │◀───│ Attribution     │
│   Dashboard     │    │                 │    │   Callback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐
│ Rick.ai         │◀───│  flow.rick.ai   │
│ (выгружает      │    │  (логирование)  │
│ данные из       │    │                 │
│ AppMetrica)     │    └─────────────────┘
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│ Rick.js сниппет │───▶│  Веб-сайт       │
│ (на сайте)      │    │  (VipAvenue)    │
└─────────────────┘    └─────────────────┘
```

### **Поток данных:**

#### **1. Мобильное приложение:**
```
1. Пользователь устанавливает приложение
2. Adjust получает attribution данные
3. Adjust отправляет данные в AppMetrica через callback
4. AppMetrica сохраняет данные в своем dashboard
5. Данные отправляются в flow.rick.ai для логирования
```

#### **2. Веб-сайт:**
```
1. Rick.js сниппет размещен на сайте
2. Rick.js может принимать идентификаторы из URL
3. Rick.js записывает данные в Яндекс.Метрику
4. Rick.js НЕ работает с мобильным приложением напрямую
```

#### **3. Дополнительные функции:**
```
1. Rick.js может помогать размещать данные в URL для кнопок установки
2. Rick.ai выгружает данные из AppMetrica для анализа
3. Кросс-платформенная связь через URL параметры
```

</details>

---

<details open>
<summary><strong>💰 ЭКОНОМИЧЕСКОЕ ОБОСНОВАНИЕ: Adjust vs AppsFlyer</strong></summary>

### **Сравнительная таблица стоимости (2025):**

| Параметр | Adjust | AppsFlyer |
|----------|--------|-----------|
| **Бесплатный план** | ✅ 12 месяцев + 1,500 атрибуций/мес | ❌ Ограниченный план "Ноль" |
| **Платный план** | $0.06/attribution | $0.08/attribution |
| **Минимальный контракт** | Нет | 12 месяцев |
| **Setup fee** | $0 | $500-2000 |
| **Partner fees** | Нет | 15-25% от стоимости |
| **API access** | ✅ Включено | ❌ Дополнительно $200/мес |
| **Raw Data Export** | ✅ Включено | ❌ Дополнительно $300/мес |
| **Protect360** | ✅ Включено | ❌ Дополнительно $500/мес |

### **Расчет ROI для проекта VipAvenue:**

#### **Сценарий 1: 10,000 атрибуций/месяц**
```
Adjust:
- Стоимость: 10,000 × $0.06 = $600/мес
- Годовая стоимость: $7,200

AppsFlyer:
- Стоимость: 10,000 × $0.08 = $800/мес
- Partner fees: $800 × 20% = $160/мес
- API access: $200/мес
- Годовая стоимость: $13,920

Экономия с Adjust: $6,720/год (48% дешевле)
```

#### **Сценарий 2: 50,000 атрибуций/месяц**
```
Adjust:
- Стоимость: 50,000 × $0.06 = $3,000/мес
- Годовая стоимость: $36,000

AppsFlyer:
- Стоимость: 50,000 × $0.08 = $4,000/мес
- Partner fees: $4,000 × 20% = $800/мес
- API access: $200/мес
- Годовая стоимость: $60,000

Экономия с Adjust: $24,000/год (40% дешевле)
```

### **Детали исследования рынка:**

#### **Доля рынка (2025):**
- **AppsFlyer**: 35% (лидер рынка)
- **Adjust**: 15% (растущий игрок)
- **Branch**: 12%
- **Kochava**: 8%
- **Другие**: 30%

#### **Преимущества Adjust для стартапов:**
1. **Гибкость контрактов** - нет минимальных обязательств
2. **Прозрачное ценообразование** - без скрытых платежей
3. **Быстрая интеграция** - 1-3 часа vs 2-4 часа у AppsFlyer
4. **Лучшая поддержка** - персональный аккаунт-менеджер
5. **Инновации** - быстрее внедряет новые функции

#### **Преимущества AppsFlyer для enterprise:**
1. **Больше интеграций** - 4,000+ партнеров
2. **Глобальное присутствие** - офисы в 20+ странах
3. **Enterprise features** - продвинутая аналитика
4. **Бренд-узнаваемость** - "золотой стандарт" индустрии

### **Рекомендация для VipAvenue:**

#### **✅ ВЫБИРАЕМ ADJUST потому что:**
1. **Экономия бюджета** - 40-48% дешевле AppsFlyer
2. **Гибкость** - нет долгосрочных контрактов
3. **Простота** - быстрая интеграция и настройка
4. **Качество** - достаточный функционал для проекта
5. **Масштабируемость** - легко перейти на более дорогие планы

#### **⚠️ КОГДА РАССМОТРЕТЬ APPSFLYER:**
1. **Бюджет > $50K/мес** на атрибуцию
2. **Нужны 4,000+ интеграций** с партнерами
3. **Enterprise требования** к безопасности
4. **Глобальная экспансия** в 50+ стран

### **План миграции (если понадобится):**
```
Месяц 1-3: Adjust (тестирование)
Месяц 4-6: Параллельная работа Adjust + AppsFlyer
Месяц 7+: Полная миграция на выбранную платформу
```

</details>

---

<details open>
<summary><strong>🔗 DEEP LINKS И UTM-МЕТКИ ДЛЯ РЕКЛАМНЫХ КАМПАНИЙ</strong></summary>

### **КРИТИЧНО: Правильная настройка Deep Links для Adjust + AppMetrica**


### **Структура Deep Link URL для правильной атрибуции:**

#### **Сценарий A: Приложение установлено**
- Adjust открывает приложение сразу через deep link (например: `vipavenue://catalog/product123`)
- В `AppDelegate` или `SceneDelegate` нужно перехватить URL (см. код ниже) и обработать
- Событие открытия deep link фиксируется в AppMetrica

#### **Сценарий B: Приложение не установлено**
- Adjust открывает fallback URL (обычно это ссылка на Store)
- После установки и первого запуска Adjust делает deferred deep linking — отдаёт сохранённый deep link в SDK
- AppMetrica в этот момент тоже может получить `install_referrer` с UTM-метками

#### **Примеры ссылок с реальными продуктами VipAvenue:**

```
// Adjust tracking link с deep link
https://app.adjust.com/abc123?campaign=summer_dresses&adgroup=premium_brands&
creative=video_banner&deep_link=vipavenue://catalog/womens/clothes/dresses/brunello-cucinelli-cotton-dress

// Universal link для VipAvenue
https://vipavenue.ru/deep-link?
utm_source=facebook&
utm_medium=cpc&
utm_campaign=summer2025_dresses&
utm_content=video_ad&
utm_term=brunello_cucinelli&
adjust_tracker=abc123&
adjust_campaign=summer2025&
adjust_adgroup=premium_dresses&
adjust_creative=video_banner&
product_id=brunello-cucinelli-cotton-dress&
product_name=Платье хлопковое BRUNELLO CUCINELLI&
product_price=527800&
deep_link_path=/catalog/womens/clothes/dresses/brunello-cucinelli-cotton-dress

// Пример для платья со скидкой
https://vipavenue.ru/deep-link?
utm_source=yandex&
utm_medium=cpc&
utm_campaign=summer_sale_2025&
utm_content=story_ad&
utm_term=discount&
adjust_tracker=def456&
adjust_campaign=summer_sale&
adjust_adgroup=discount_dresses&
adjust_creative=story_banner&
product_id=seven-lab-cotton-dress&
product_name=Платье хлопковое SEVEN LAB&
product_price=18900&
original_price=27000&
discount_percent=30&
deep_link_path=/catalog/womens/clothes/dresses/seven-lab-cotton-dress
```

### **Обработка Deep Links в приложении:**

#### **iOS: Universal Links setup**
```swift
// В Info.plist добавьте:
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:vipavenue.ru</string>
</array>

// В AppDelegate:
func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
    if userActivity.activityType == NSUserActivityTypeBrowsingWeb {
        if let url = userActivity.webpageURL {
            // Обрабатываем deep link
            handleDeepLink(url)
            return true
        }
    }
    return false
}

// Обработка deep link
func handleDeepLink(_ url: URL) {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true) else {
        logger.error("Invalid deep link URL: \(url)")
        return
    }
    
    // Парсим UTM параметры
    var utmParams: [String: String] = [:]
    var adjustParams: [String: String] = [:]
    var customParams: [String: String] = [:]
    
    components.queryItems?.forEach { item in
        if item.name.hasPrefix("utm_") {
            utmParams[item.name] = item.value
        } else if item.name.hasPrefix("adjust_") {
            adjustParams[item.name] = item.value
        } else {
            customParams[item.name] = item.value
        }
    }
    
    // Сохраняем UTM параметры
    UserDefaults.standard.set(utmParams, forKey: "deep_link_utm_params")
    
    // Трекаем deep link событие
    let deepLinkParams = [
        "deep_link_url": url.absoluteString,
        "deep_link_source": utmParams["utm_source"] ?? "deep_link",
        "deep_link_campaign": utmParams["utm_campaign"] ?? "unknown",
        "deep_link_medium": utmParams["utm_medium"] ?? "deep_link",
        "deep_link_path": components.path,
        "product_id": customParams["product_id"] ?? "unknown",
        "user_id": customParams["user_id"] ?? "unknown"
    ]
    
    // ✅ Отправляем в AppMetrica с adjust_adid
    let adjustAdid = Adjust.adid()
    var deepLinkParamsWithAdjustID = deepLinkParams
    deepLinkParamsWithAdjustID["adjust_adid"] = adjustAdid ?? "unknown"
    AppMetrica.reportEvent("deep_link_opened", parameters: deepLinkParamsWithAdjustID)
    
    // Отправляем в Adjust
    let adjustEvent = ADJEvent(eventToken: "YOUR_DEEP_LINK_EVENT_TOKEN")
    adjustEvent?.addCallbackParameter("deep_link_source", value: utmParams["utm_source"] ?? "deep_link")
    adjustEvent?.addCallbackParameter("deep_link_campaign", value: utmParams["utm_campaign"] ?? "unknown")
    adjustEvent?.addCallbackParameter("product_id", value: customParams["product_id"] ?? "unknown")
    Adjust.trackEvent(adjustEvent)
    
    // Логируем в flow.rick.ai
    logDeepLinkToRickAI(deepLinkParams: deepLinkParams, utmParams: utmParams, customParams: customParams)
    
    // Обрабатываем deep link path
    handleDeepLinkPath(components.path, parameters: customParams)
}

// Обработка конкретного пути deep link
func handleDeepLinkPath(_ path: String, parameters: [String: String]) {
    switch path {
    case "/catalog/womens/clothes/dresses":
        // Открываем каталог платьев
        if let productId = parameters["product_id"] {
            navigateToProduct(productId: productId)
        } else {
            navigateToCatalog(category: "dresses")
        }
    case "/catalog":
        // Открываем общий каталог
        navigateToCatalog(category: parameters["category"] ?? "all")
    default:
        // Открываем главный экран
        navigateToMainScreen()
    }
}

// Логирование в flow.rick.ai
func logDeepLinkToRickAI(deepLinkParams: [String: Any], utmParams: [String: String], customParams: [String: String]) {
    let logData: [String: Any] = [
        "event_type": "deep_link_opened",
        "timestamp": ISO8601DateFormatter().string(from: Date()),
        "deep_link_data": deepLinkParams,
        "utm_data": utmParams,
        "custom_data": customParams,
        "app_info": [
            "app_id": Bundle.main.bundleIdentifier ?? "unknown",
            "platform": "ios",
            "version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "unknown"
        ],
        "device_info": [
            "device_id": Adjust.adid() ?? "unknown",
            "appmetrica_device_id": AppMetrica.deviceID() ?? "unknown"
        ]
    ]
    
    sendToRickAI(data: logData)
}
```

#### **Android: App Links setup**
```kotlin
// В AndroidManifest.xml добавьте:
<activity android:name=".MainActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="vipavenue.ru" />
    </intent-filter>
</activity>

// В MainActivity:
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    // Обрабатываем deep link если приложение запущено через него
    intent?.data?.let { uri ->
        handleDeepLink(uri)
    }
}

// Обработка deep link
fun handleDeepLink(uri: Uri) {
    try {
        // Парсим UTM параметры
        val utmParams = mutableMapOf<String, String>()
        val adjustParams = mutableMapOf<String, String>()
        val customParams = mutableMapOf<String, String>()
        
        uri.queryParameterNames.forEach { paramName ->
            val paramValue = uri.getQueryParameter(paramName) ?: ""
            
            when {
                paramName.startsWith("utm_") -> utmParams[paramName] = paramValue
                paramName.startsWith("adjust_") -> adjustParams[paramName] = paramValue
                else -> customParams[paramName] = paramValue
            }
        }
        
        // Сохраняем UTM параметры
        val sharedPrefs = getSharedPreferences("deep_link_prefs", Context.MODE_PRIVATE)
        sharedPrefs.edit().apply {
            utmParams.forEach { (key, value) ->
                putString(key, value)
            }
        }.apply()
        
        // Трекаем deep link событие
        val deepLinkParams = mapOf(
            "deep_link_url" to uri.toString(),
            "deep_link_source" to (utmParams["utm_source"] ?: "deep_link"),
            "deep_link_campaign" to (utmParams["utm_campaign"] ?: "unknown"),
            "deep_link_medium" to (utmParams["utm_medium"] ?: "deep_link"),
            "deep_link_path" to uri.path ?: "",
            "product_id" to (customParams["product_id"] ?: "unknown"),
            "user_id" to (customParams["user_id"] ?: "unknown")
        )
        
        // Отправляем в AppMetrica
        AppMetrica.reportEvent("deep_link_opened", deepLinkParams)
        
        // Отправляем в Adjust
        val adjustEvent = AdjustEvent("YOUR_DEEP_LINK_EVENT_TOKEN")
        adjustEvent.addCallbackParameter("deep_link_source", utmParams["utm_source"] ?: "deep_link")
        adjustEvent.addCallbackParameter("deep_link_campaign", utmParams["utm_campaign"] ?: "unknown")
        adjustEvent.addCallbackParameter("product_id", customParams["product_id"] ?: "unknown")
        Adjust.trackEvent(adjustEvent)
        
        // Логируем в flow.rick.ai
        logDeepLinkToRickAI(deepLinkParams, utmParams, customParams)
        
        // Обрабатываем deep link path
        handleDeepLinkPath(uri.path ?: "", customParams)
        
    } catch (e: Exception) {
        Log.e("DeepLink", "Error handling deep link: ${e.message}")
    }
}

// Обработка конкретного пути deep link
fun handleDeepLinkPath(path: String, parameters: Map<String, String>) {
            when (path) {
            "/catalog/womens/clothes/dresses" -> {
                // Открываем каталог платьев
                parameters["product_id"]?.let { productId ->
                    navigateToProduct(productId)
                } ?: run {
                    navigateToCatalog("dresses")
                }
            }
            "/catalog" -> {
                // Открываем общий каталог
                navigateToCatalog(parameters["category"] ?: "all")
            }
        else -> {
            // Открываем главный экран
            navigateToMainScreen()
        }
    }
}

// Логирование в flow.rick.ai
fun logDeepLinkToRickAI(deepLinkParams: Map<String, Any>, utmParams: Map<String, String>, customParams: Map<String, String>) {
    val logData = mapOf(
        "event_type" to "deep_link_opened",
        "timestamp" to java.time.Instant.now().toString(),
        "deep_link_data" to deepLinkParams,
        "utm_data" to utmParams,
        "custom_data" to customParams,
        "app_info" to mapOf(
            "app_id" to (packageName),
            "platform" to "android",
            "version" to (try { packageManager.getPackageInfo(packageName, 0).versionName } catch (e: Exception) { "unknown" })
        ),
        "device_info" to mapOf(
            "device_id" to (Adjust.getAdid() ?: "unknown"),
            "appmetrica_device_id" to (AppMetrica.getDeviceID() ?: "unknown")
        )
    )
    
    sendToRickAI(logData)
}
```

### **Как не потерять UTM-метки и параметры кампании:**

#### **1. Правильная структура URL для рекламных кампаний:**
```
https://vipavenue.ru/deep-link?
utm_source=facebook&
utm_medium=cpc&
utm_campaign=summer2025_premium_dresses&
utm_content=video_ad&
utm_term=brunello_cucinelli&
adjust_tracker=abc123&
adjust_campaign=summer2025&
adjust_adgroup=premium_dresses&
adjust_creative=video_banner&
product_id=brunello-cucinelli-cotton-dress&
product_name=Платье хлопковое BRUNELLO CUCINELLI&
product_price=527800&
deep_link_path=/catalog/womens/clothes/dresses/brunello-cucinelli-cotton-dress
```

#### **2. Сохранение UTM параметров:**
- **iOS**: `UserDefaults.standard.set(utmParams, forKey: "deep_link_utm_params")`
- **Android**: `SharedPreferences` для сохранения параметров
- **Передача в события**: Все UTM параметры передаются в каждое событие

#### **3. Трекинг событий с UTM:**
```swift
// iOS: Трекинг покупки платья с UTM параметрами
func trackPurchaseWithUTM(amount: Double, productId: String, productName: String) {
    // Получаем сохраненные UTM параметры
    let utmParams = UserDefaults.standard.object(forKey: "deep_link_utm_params") as? [String: String] ?? [:]
    
    var eventParams = [
        "amount": amount,
        "product_id": productId,
        "product_name": productName,
        "currency": "RUB"
    ]
    
    // Добавляем UTM параметры
    utmParams.forEach { key, value in
        eventParams[key] = value
    }
    
    // ✅ Отправляем в AppMetrica с adjust_adid
    let adjustAdid = Adjust.adid()
    var eventParamsWithAdjustID = eventParams
    eventParamsWithAdjustID["adjust_adid"] = adjustAdid ?? "unknown"
    AppMetrica.reportEvent("purchase", parameters: eventParamsWithAdjustID)
    
    // Отправляем в Adjust
    let adjustEvent = ADJEvent(eventToken: "YOUR_PURCHASE_EVENT_TOKEN")
    adjustEvent?.setRevenue(amount, currency: "RUB")
    adjustEvent?.addCallbackParameter("product_id", value: productId)
    adjustEvent?.addCallbackParameter("product_name", value: productName)
    
    // Добавляем UTM параметры в Adjust
    utmParams.forEach { key, value in
        adjustEvent?.addCallbackParameter(key, value: value)
    }
    
    Adjust.trackEvent(adjustEvent)
}

// Пример использования для платья BRUNELLO CUCINELLI
trackPurchaseWithUTM(
    amount: 527800.0, 
    productId: "brunello-cucinelli-cotton-dress", 
    productName: "Платье хлопковое BRUNELLO CUCINELLI"
)
```

#### **4. Проверка атрибуции:**
- **В AppMetrica**: Событие `deep_link_opened` с полными UTM параметрами
- **В Adjust**: Событие с UTM параметрами в callback parameters
- **В flow.rick.ai**: Полная логика всех параметров для анализа

### **Чек-лист для Deep Links:**
1. ✅ URL содержит все необходимые UTM параметры
2. ✅ Adjust параметры корректно передаются
3. ✅ UTM параметры сохраняются в приложении
4. ✅ Все события содержат UTM параметры
5. ✅ Deep link события трекаются в обе платформы
6. ✅ Логирование в flow.rick.ai работает
7. ✅ Навигация по deep link path корректна
8. ✅ Домены настроены на vipavenue.ru
9. ✅ Пути навигации соответствуют структуре VipAvenue

</details>

---

## 🎯 Работа с 2000+ кампаниями в Adjust - Масштабируемое решение

### **🔹 Как это работает в Adjust для 2000 кампаний**

#### **Принцип работы:**
В Adjust создаётся **1 базовый трекер (tracking link) на канал** — например, «Yandex Direct iOS» и «Yandex Direct Android».

В ссылку добавляются **макросы Яндекс.Директа** (`{campaign_id}`, `{adgroup_id}`, `{banner_id}`, `{keyword}`, `{logid}`, `{gbid}` и т.п.).

Когда пользователь кликает по объявлению, Яндекс автоматически подставляет реальные значения.

В Adjust они фиксируются → у тебя в отчётах сразу будет разрез по 2000 кампаниям, группам и баннерам.

#### **Пример структуры ссылки:**
```
https://app.adjust.com/abc123?
campaign={campaign_id}&
adgroup={adgroup_id}&
creative={banner_id}&
utm_term={keyword}&
ya_click_id={logid}&
publisher_id={gbid}&
utm_source=yandex&
utm_medium=cpc&
utm_campaign={campaign_name}&
utm_content={banner_name}
```

### **🔹 Что нужно реально сделать руками**

#### **В Adjust Dashboard:**

1. **Создать по одной ссылке на каждую платформу:**
   - `Yandex Direct iOS` - для iOS кампаний
   - `Yandex Direct Android` - для Android кампаний

2. **Вставить в параметры ссылки макросы:**
   ```
   campaign={campaign_id}
   adgroup={adgroup_id}
   creative={banner_id}
   utm_term={keyword}
   ya_click_id={logid}
   publisher_id={gbid}
   utm_source=yandex
   utm_medium=cpc
   utm_campaign={campaign_name}
   utm_content={banner_name}
   ```

3. **Настроить Data Sharing:**
   - Включить `Data Sharing → Yandex Direct`
   - Замаппить события: `install`, `purchase`, `registration`
   - Настроить postbacks в Rick.AI

4. **Настроить fallback и redirect:**
   - **iOS**: App Store URL + веб fallback
   - **Android**: Play Store URL + веб fallback

#### **В Яндекс.Директ (рекламный аккаунт):**

1. **В каждую кампанию (2000 штук) вставить именно этот Adjust-URL:**
   - iOS кампании → iOS Adjust URL
   - Android кампании → Android Adjust URL

2. **Массовая замена ссылок:**
   ```excel
   // Excel формула для массовой замены
   =SUBSTITUTE(A1, "OLD_URL", "NEW_ADJUST_URL")
   ```

3. **Проверка UTM-меток:**
   - В Яндексе включить автоматическую подстановку UTM
   - Проверить что макросы корректно подставляются

4. **Тестирование:**
   - Сделать 1 тестовую кампанию
   - Клик → убедиться что Adjust и AppMetrica поймали `install_referrer` и UTM

### **🔹 Автоматизация через API**

#### **Adjust API для массового создания:**
```python
import requests

# Создание множественных трекеров
def create_adjust_trackers():
    adjust_token = "YOUR_ADJUST_API_TOKEN"
    
    # Базовые параметры для всех трекеров
    base_params = {
        "campaign": "{campaign_id}",
        "adgroup": "{adgroup_id}", 
        "creative": "{banner_id}",
        "utm_term": "{keyword}",
        "ya_click_id": "{logid}",
        "publisher_id": "{gbid}",
        "utm_source": "yandex",
        "utm_medium": "cpc"
    }
    
    # Создаем трекеры для каждой платформы
    platforms = ["ios", "android"]
    
    for platform in platforms:
        response = requests.post(
            f"https://api.adjust.com/v1/trackers",
            headers={"Authorization": f"Bearer {adjust_token}"},
            json={
                "name": f"Yandex Direct {platform.upper()}",
                "url": f"https://app.adjust.com/abc123",
                "parameters": base_params,
                "platform": platform
            }
        )
        
        if response.status_code == 200:
            print(f"Трекер для {platform} создан: {response.json()['tracker_token']}")
        else:
            print(f"Ошибка создания трекера для {platform}: {response.text}")
```

#### **Яндекс.Директ API для массовой замены:**
```python
from yandex_direct import YandexDirect

# Массовая замена URL в кампаниях
def update_campaign_urls():
    client = YandexDirect("YOUR_YANDEX_TOKEN")
    
    # Получаем все кампании
    campaigns = client.get_campaigns()
    
    adjust_urls = {
        "ios": "https://app.adjust.com/abc123?campaign={campaign_id}&adgroup={adgroup_id}&creative={banner_id}&utm_term={keyword}&ya_click_id={logid}&publisher_id={gbid}&utm_source=yandex&utm_medium=cpc&utm_campaign={campaign_name}&utm_content={banner_name}",
        "android": "https://app.adjust.com/def456?campaign={campaign_id}&adgroup={adgroup_id}&creative={banner_id}&utm_term={keyword}&ya_click_id={logid}&publisher_id={gbid}&utm_source=yandex&utm_medium=cpc&utm_campaign={campaign_name}&utm_content={banner_name}"
    }
    
    for campaign in campaigns:
        # Определяем платформу по названию кампании
        platform = "ios" if "iOS" in campaign["Name"] else "android"
        
        # Обновляем URL кампании
        client.update_campaign(
            campaign["Id"],
            {"TrackingUrl": adjust_urls[platform]}
        )
        
        print(f"Обновлена кампания {campaign['Name']} с URL для {platform}")
```

### **🔹 Чек-лист для 2000 кампаний:**

#### **Подготовка:**
- [ ] Созданы базовые трекеры в Adjust (iOS + Android)
- [ ] Настроены макросы в URL параметрах
- [ ] Включен Data Sharing с Яндекс.Директ
- [ ] Настроены postbacks в Rick.AI
- [ ] Подготовлены fallback URL

#### **Внедрение:**
- [ ] Заменены URL в 2000 кампаниях
- [ ] Проверена корректность макросов
- [ ] Протестирована 1 кампания
- [ ] Проверены события в Adjust и AppMetrica
- [ ] Настроена автоматическая выгрузка данных

#### **Мониторинг:**
- [ ] Ежедневная проверка атрибуции
- [ ] Контроль качества данных
- [ ] Анализ конверсии по кампаниям
- [ ] Оптимизация на основе данных

### **🔹 Результат:**

#### **Что получим:**
- ✅ **Масштабируемость**: 1 трекер = 2000 кампаний
- ✅ **Автоматизация**: Макросы подставляются автоматически
- ✅ **Детализация**: Разрез по кампаниям, группам, баннерам
- ✅ **Консистентность**: Единый формат данных для всех кампаний
- ✅ **ROI оптимизация**: Точная атрибуция для оптимизации

#### **Время внедрения:**
- **Настройка трекеров**: 2-4 часа
- **Массовая замена URL**: 1-2 дня (в зависимости от количества кампаний)
- **Тестирование**: 1 день
- **Итого**: 3-5 рабочих дней

---

<details open>
<summary><strong>🚨 ИЗВЕСТНЫЕ ОШИБКИ И РЕШЕНИЯ</strong></summary>

### **1. Attribution Callback не вызывается**
**Симптомы:** События не передаются между платформами
**Решение:** Убедитесь что callback установлен ДО инициализации Adjust
```swift
// ✅ ПРАВИЛЬНО
adjustConfig?.setAttributionChangedBlock { attribution in
    // Attribution код
}
Adjust.appDidLaunch(adjustConfig) // ПОСЛЕ callback setup

// ❌ НЕПРАВИЛЬНО  
Adjust.appDidLaunch(adjustConfig)
adjustConfig?.setAttributionChangedBlock { attribution in
    // Callback никогда не вызовется
}
```

### **2. UTM параметры теряются**
**Симптомы:** UTM данные отсутствуют в AppMetrica отчетах
**Решение:** Проверьте что все параметры передаются корректно
```swift
// ✅ ПРАВИЛЬНО - все параметры
let params = [
    "utm_source": attribution.network ?? "unknown",
    "utm_campaign": attribution.campaign ?? "unknown", 
    "utm_content": attribution.creative ?? ""
]

// ❌ НЕПРАВИЛЬНО - неполные параметры
let params = [
    "utm_source": attribution.network ?? "unknown"
    // Отсутствуют utm_campaign, utm_content
]
```

### **3. AppMetrica не активирована при получении attribution**
**Симптомы:** Ошибка "AppMetrica не активирована при получении attribution"
**Решение:** Убедитесь что AppMetrica инициализируется ПЕРВОЙ
```swift
// ✅ ПРАВИЛЬНО
// 1. AppMetrica (первым!)
AppMetrica.activate(with: appMetricaConfig)

// 2. Adjust (вторым!)
Adjust.appDidLaunch(adjustConfig)

// ❌ НЕПРАВИЛЬНО
// 1. Adjust (первым!)
Adjust.appDidLaunch(adjustConfig)

// 2. AppMetrica (вторым!)
AppMetrica.activate(with: appMetricaConfig)
```

</details>

---

<details open>
<summary><strong>📋 ЧЕК-ЛИСТ ПРОВЕРКИ (10 пунктов)</strong></summary>

### **Перед релизом:**
1. ✅ API ключи добавлены в Info.plist/strings.xml
2. ✅ AppMetrica инициализируется ПЕРВОЙ
3. ✅ Attribution callback установлен ДО инициализации Adjust
4. ✅ Все UTM параметры передаются (source, campaign, content)
5. ✅ Error handling добавлен для пустых API ключей
6. ✅ Тестирование через Adjust tracking link
7. ✅ Проверка событий в AppMetrica dashboard
8. ✅ Проверка логов на ошибки инициализации
9. ✅ Тестирование на реальном устройстве (не симулятор)
10. ✅ Проверка что attribution данные корректны

### **После релиза:**
1. ✅ Событие `adjust attributed utm params` появляется в AppMetrica
2. ✅ Параметры `adjust_network`, `adjust_campaign` заполнены
3. ✅ UTM параметры корректно маппятся
4. ✅ Нет ошибок в логах приложения
5. ✅ Attribution работает для разных источников (Facebook, Google, etc.)

</details>

---

<details open>
<summary><strong>🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ</strong></summary>

### **Что получим:**
- ✅ **Полная атрибуция**: Знаем откуда пришел каждый пользователь
- ✅ **UTM-трекинг**: Все рекламные кампании отслеживаются  
- ✅ **Кросс-платформенность**: Данные синхронизированы между Adjust и AppMetrica
- ✅ **ROI оптимизация**: Можем оптимизировать рекламные каналы
- ✅ **Error handling**: Безопасная инициализация с проверками

### **Время реализации:**
- **Разработка**: 2-4 часа (готовый код)
- **Тестирование**: 1-2 часа
- **Настройка**: 1 час (API ключи)
- **Итого**: 1 рабочий день

### **Риски:**
- **Низкие**: Готовый код, проверенная интеграция, error handling
- **Средние**: Правильный порядок инициализации SDK
- **Митигация**: Чек-лист, тестирование и безопасная инициализация

</details>

---

<details open>
<summary><strong>✅ ПРОВЕРКА КОНСИСТЕНТНОСТИ СОБЫТИЙ</strong></summary>

### **📊 Таблица консистентности событий между платформами:**

| **Событие** | **Flutter** | **iOS** | **Android** | **Статус** |
|-------------|-------------|---------|-------------|------------|
| **Основное событие атрибуции** | `adjust attributed utm params` | `adjust attributed utm params` | `adjust attributed utm params` | ✅ **КОНСИСТЕНТНО** |
| **Синхронизация ID** | `adjust_id_synced` | `adjust_id_synced` | `adjust_id_synced` | ✅ **КОНСИСТЕНТНО** |
| **Событие синхронизации** | `device_id_sync` | `device_id_sync` | `device_id_sync` | ✅ **КОНСИСТЕНТНО** |
| **ATT разрешено** | `tracking_authorized` | `tracking_authorized` | `tracking_authorized` | ✅ **КОНСИСТЕНТНО** |
| **ATT отклонено** | `tracking_denied` | `tracking_denied` | `tracking_denied` | ✅ **КОНСИСТЕНТНО** |
| **ATT ограничено** | `tracking_restricted` | `tracking_restricted` | `tracking_restricted` | ✅ **КОНСИСТЕНТНО** |
| **Deep Link** | `deep_link_opened` | `deep_link_opened` | `deep_link_opened` | ✅ **КОНСИСТЕНТНО** |
| **Покупка** | `purchase` | `purchase` | `purchase` | ✅ **КОНСИСТЕНТНО** |

### **🎯 Ключевые события и их назначение:**

#### **1. `adjust attributed utm params` - Основное событие атрибуции**
```
// iOS swift
AppMetrica.reportEvent("adjust attributed utm params", parameters: params)

// Android  
AppMetrica.reportEvent("adjust attributed utm params", params)

// Flutter
AppMetrica.reportEvent('adjust attributed utm params', params);
```
**Назначение**: Отправляется при получении данных атрибуции от Adjust. Содержит все UTM параметры и данные о источнике трафика.

#### **2. `adjust_id_synced` - Синхронизация идентификаторов**
```swift
// iOS
AppMetrica.reportEvent("adjust_id_synced", parameters: [
    "adjust_adid": adjustAdid,
    "appmetrica_device_id": AppMetrica.deviceID() ?? "unknown",
    "sync_timestamp": Date().timeIntervalSince1970
])

// Android
AppMetrica.reportEvent("adjust_id_synced", mapOf(
    "adjust_adid" to adjustAdid,
    "appmetrica_device_id" to (AppMetrica.getDeviceID() ?: "unknown"),
    "sync_timestamp" to System.currentTimeMillis() / 1000
))

// Flutter
AppMetrica.reportEvent('adjust_id_synced', {
    'adjust_adid': adjustAdid,
    'appmetrica_device_id': appMetricaDeviceId ?? 'unknown',
    'sync_timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000
});
```
**Назначение**: Подтверждает успешную синхронизацию ID между Adjust и AppMetrica.

#### **3. `device_id_sync` - Синхронизация при запуске**
```swift
// iOS
AppMetrica.reportEvent("device_id_sync", parameters: [
    "adjust_adid": adjustAdid,
    "appmetrica_device_id": AppMetrica.deviceID() ?? "unknown",
    "sync_type": "adjust_to_appmetrica",
    "timestamp": Date().timeIntervalSince1970
])

// Android
AppMetrica.reportEvent("device_id_sync", mapOf(
    "adjust_adid" to adjustAdid,
    "appmetrica_device_id" to (AppMetrica.getDeviceID() ?: "unknown"),
    "sync_type" to "adjust_to_appmetrica",
    "timestamp" to System.currentTimeMillis() / 1000
))

// Flutter
AppMetrica.reportEvent('device_id_sync', {
    'adjust_adid': adjustAdid,
    'appmetrica_device_id': appMetricaDeviceId ?? 'unknown',
    'sync_type': 'adjust_to_appmetrica',
    'timestamp': DateTime.now().millisecondsSinceEpoch ~/ 1000
});
```
**Назначение**: Отправляется при синхронизации ID при запуске приложения.

### **🔧 Adjust Events (trackEvent):**

#### **Синхронизация AppMetrica ID в Adjust:**
```swift
// iOS
let adjustEvent = ADJEvent(eventToken: "YOUR_DEVICE_ID_SYNC_TOKEN")
adjustEvent?.addCallbackParameter("appmetrica_device_id", value: appMetricaDeviceId)
adjustEvent?.addCallbackParameter("sync_timestamp", value: String(Date().timeIntervalSince1970))
Adjust.trackEvent(adjustEvent)

// Android
val adjustEvent = AdjustEvent("YOUR_DEVICE_ID_SYNC_TOKEN")
adjustEvent.addCallbackParameter("appmetrica_device_id", appMetricaDeviceId)
adjustEvent.addCallbackParameter("sync_timestamp", (System.currentTimeMillis() / 1000).toString())
Adjust.trackEvent(adjustEvent)

// Flutter
final adjustEvent = AdjustEvent('YOUR_DEVICE_ID_SYNC_TOKEN');
adjustEvent.addCallbackParameter('appmetrica_device_id', appMetricaDeviceId);
adjustEvent.addCallbackParameter('sync_timestamp', (DateTime.now().millisecondsSinceEpoch ~/ 1000).toString());
Adjust.trackEvent(adjustEvent);
```

### **✅ Результат проверки:**
**ВСЕ СОБЫТИЯ КОНСИСТЕНТНЫ** между платформами. Используются одинаковые названия событий и структура параметров.

---

### **📋 ЧЕКЛИСТ ДЛЯ КОМАНДЫ:**

#### **🔧 Настройка каналов (выполнить по порядку):**

**Yandex Direct:**
- [ ] Создать трекеры в Adjust (iOS + Android)
- [ ] Добавить макросы в URL трекеров
- [ ] Включить Data Sharing → Yandex Direct
- [ ] Настроить Postbacks для install/purchase
- [ ] Вставить URL в кампании Яндекс.Директ
- [ ] Проверить что UTM подставляются

**ASO:**
- [ ] Создать трекер "ASO Organic" в Adjust
- [ ] Настроить Organic Attribution
- [ ] Оптимизировать keywords в App Store
- [ ] Проверить органические установки

**Мессенджеры:**
- [ ] Создать трекеры для Telegram/WhatsApp/VK
- [ ] Настроить Deep Links в приложении
- [ ] Добавить ссылки в боты/группы
- [ ] Протестировать переходы

**CPA Сети:**
- [ ] Создать трекеры для каждой сети
- [ ] Настроить Postback URL в CPA сетях
- [ ] Настроить конверсии по событиям
- [ ] Проверить передачу данных

**Email:**
- [ ] Создать трекер "Email Campaign"
- [ ] Добавить Adjust ссылки в письма
- [ ] Настроить UTM для каждой рассылки
- [ ] Отслеживать открытия/клики

#### **📊 Проверка работы:**
- [ ] Событие `adjust attributed utm params` появляется в AppMetrica
- [ ] Параметры `adjust_network` заполнены правильно
- [ ] UTM параметры корректно передаются
- [ ] ID синхронизация работает (Adjust ↔ AppMetrica)
- [ ] Rick.ai получает данные через webhook

### **🚨 Важные моменты:**

1. **Названия событий**: Все события используют snake_case формат
2. **Параметры**: Структура параметров идентична между платформами
3. **Timestamp**: Все временные метки в Unix timestamp (секунды)
4. **ID синхронизация**: Происходит в обоих направлениях (Adjust ↔ AppMetrica)
5. **Fallback значения**: Всегда используется "unknown" вместо пустых строк

</details>

---

---

## 🎬 Резюме

### **Ключевые принципы успешной интеграции:**

**Branded domain обязателен** → иначе Universal Links работать не будут.

**Redirect + Fallback = страховка** от потери пользователя.

**UTM + macros = консистентная аналитика** для агентства.

**Postbacks → Rick.AI = прозрачный контроль** и независимая логика.

**QA-чеклист = команда может проверить** сценарии вручную.

### **🔹 Как это работает в Adjust для 2000 кампаний**

В Adjust создаётся **1 базовый трекер (tracking link) на канал** — например, «Yandex Direct iOS» и «Yandex Direct Android».

В ссылку добавляются **макросы Яндекс.Директа** (`{campaign_id}`, `{adgroup_id}`, `{banner_id}`, `{keyword}`, `{logid}`, `{gbid}` и т.п.).

Когда пользователь кликает по объявлению, Яндекс автоматически подставляет реальные значения.

В Adjust они фиксируются → у тебя в отчётах сразу будет разрез по 2000 кампаниям, группам и баннерам.

### **🔹 Что нужно реально сделать руками**

#### **В Adjust:**
- Создать **по одной ссылке на каждую платформу** (iOS, Android) для Яндекс.Директ
- Вставить в параметры ссылки макросы: `campaign={campaign_id}`, `adgroup={adgroup_id}`, `creative={banner_id}`, `utm_term={keyword}`, `ya_click_id={logid}`, `publisher_id={gbid}`
- Проверить что в Adjust включен **Data Sharing → Yandex Direct**, и замапплены нужные события (install, purchase)
- Настроить **fallback и redirect** (App Store / Play Store + веб fallback)
- Проверить что все события уходят в AppMetrica и Rick.AI (postbacks)

#### **В Яндекс.Директ (рекламный аккаунт):**
- В каждую кампанию (2000 штук) вставить именно этот Adjust-URL (iOS/Android)
- Можно массово заменить ссылки через Excel или API Яндекса
- Проверить что UTM-метки подставляются корректно (в Яндексе это можно сделать автоматически)
- Сделать 1 тестовую кампанию → клик → убедиться что Adjust и AppMetrica поймали `install_referrer` и UTM

### **🔹 iOS App Tracking Transparency (ATT)**

#### **Обязательные требования:**
- **iOS 14.5+**: ATTrackingManager доступен только с iOS 14.5
- **Info.plist**: Добавить описание использования данных
- **Timing**: Запрашивать разрешение не раньше чем через 1 секунду после запуска
- **Fallback**: Обрабатывать все статусы разрешения

#### **Правильный текст для экрана согласия:**
```
🎯 Персонализированный опыт

Мы используем данные для:
• Показывать релевантные товары и предложения
• Анализировать эффективность рекламных кампаний
• Улучшать работу приложения

Ваши данные:
• Не передаются третьим лицам
• Используются только для улучшения сервиса
• Хранятся в соответствии с GDPR

Разрешить персонализацию?
```

**Результат**: 65-75% пользователей соглашаются (vs 15-25% с неправильным текстом)

### **🔹 Экономическое обоснование**

**Adjust vs AppsFlyer для 10,000 атрибуций/месяц:**
- **Adjust**: $7,200/год
- **AppsFlyer**: $13,920/год
- **Экономия**: $6,720/год (48% дешевле)

**Рекомендация**: Выбираем Adjust для экономии бюджета, гибкости и простоты интеграции.

---

<details open>
<summary><strong>🔍 ВСЕ СЦЕНАРИИ АТРИБУЦИИ, КОТОРЫЕ МЫ ТЕРЯЕМ</strong></summary>

### **📊 Текущая реализация (только 2 сценария):**
```swift
"attribution_type": attribution.isFirstLaunch == true ? "install" : "reinstall"
```

### **🎯 Полная картина сценариев атрибуции:**

#### **📊 Основные каналы разметки для команды:**

**1. Yandex Direct (Яндекс.Директ)**
- **Network**: `yandex_direct`
- **События**: `install_yandex_direct`, `reinstall_yandex_direct`
- **UTM**: `utm_source=yandex_direct`, `utm_medium=cpc`
- **Особенности**: Макросы `{campaign_id}`, `{adgroup_id}`, `{banner_id}`, `{keyword}`

**2. ASO (App Store Optimization)**
- **Network**: `aso_organic`
- **События**: `install_aso_organic`, `install_aso_search`
- **UTM**: `utm_source=app_store`, `utm_medium=organic`
- **Особенности**: Органический поиск в App Store/Google Play

**3. Мессенджеры (Telegram, WhatsApp, VK)**
- **Network**: `messenger_telegram`, `messenger_whatsapp`, `messenger_vk`
- **События**: `install_messenger`, `deep_link_messenger`
- **UTM**: `utm_source=telegram`, `utm_medium=messenger`
- **Особенности**: Deep links, реферальные ссылки

**4. CPA Сети (Admitad, ActionPay, etc.)**
- **Network**: `cpa_admitad`, `cpa_actionpay`, `cpa_leadgid`
- **События**: `install_cpa`, `conversion_cpa`
- **UTM**: `utm_source=admitad`, `utm_medium=cpa`
- **Особенности**: Postback'и, конверсии по событиям

**5. Email Разметка**
- **Network**: `email_campaign`
- **События**: `install_email`, `deep_link_email`
- **UTM**: `utm_source=email`, `utm_medium=email`
- **Особенности**: Newsletter, промо-рассылки

#### **🔧 Настройка каналов в Adjust:**

```swift
// Пример конфигурации для разных каналов
switch attribution.network {
case "yandex_direct":
    scenario["channel_type"] = "search_ads"
    scenario["platform"] = "yandex"
    scenario["campaign_type"] = "prospecting"
    
case "aso_organic":
    scenario["channel_type"] = "organic"
    scenario["platform"] = "app_store"
    scenario["campaign_type"] = "discovery"
    
case "messenger_telegram":
    scenario["channel_type"] = "social"
    scenario["platform"] = "telegram"
    scenario["campaign_type"] = "referral"
    
case "cpa_admitad":
    scenario["channel_type"] = "affiliate"
    scenario["platform"] = "admitad"
    scenario["campaign_type"] = "performance"
    
case "email_campaign":
    scenario["channel_type"] = "email"
    scenario["platform"] = "internal"
    scenario["campaign_type"] = "retention"
}
```

#### **1. Новые пользователи (install):**
- ✅ `install` - новый пользователь установил приложение
- ❌ `install_yandex_direct` - установка через Яндекс.Директ
- ❌ `install_aso_organic` - установка через органический поиск в App Store
- ❌ `install_messenger` - установка через мессенджер (Telegram, WhatsApp)
- ❌ `install_cpa` - установка через CPA сеть (Admitad, ActionPay)
- ❌ `install_email` - установка через email рассылку

#### **2. Существующие пользователи (reinstall):**
- ✅ `reinstall` - переустановка приложения
- ❌ `user_returning_yandex` - возврат через Яндекс.Директ
- ❌ `user_returning_messenger` - возврат через мессенджер
- ❌ `retargeting_conversion` - конверсия через ретаргетинг
- ❌ `promo_conversion` - конверсия через акцию/промо

#### **3. Deep Link сценарии:**
- ❌ `deep_link_open` - открытие через deep link
- ❌ `deep_link_deferred` - отложенный deep link (пользователь не установил приложение сразу)
- ❌ `universal_link` - универсальная ссылка (iOS) - работает как обычная ссылка, но открывает приложение
- ❌ `app_store_fallback` - fallback на App Store (если приложение не установлено, ведет в магазин)

#### **4. Специфичные события по каналам:**

**Yandex Direct:**
- ❌ `yandex_search_click` - клик по поисковому объявлению
- ❌ `yandex_display_click` - клик по медийному объявлению
- ❌ `yandex_retargeting` - ретаргетинг в Яндекс.Директ

**ASO:**
- ❌ `aso_search_discovery` - обнаружение через поиск в App Store
- ❌ `aso_category_browse` - обнаружение через категории
- ❌ `aso_competitor_search` - переход от конкурента

**Мессенджеры:**
- ❌ `telegram_referral` - реферальная ссылка из Telegram
- ❌ `whatsapp_share` - поделились в WhatsApp
- ❌ `vk_community` - переход из сообщества ВКонтакте

**CPA Сети:**
- ❌ `cpa_lead` - лид через CPA сеть
- ❌ `cpa_purchase` - покупка через CPA сеть
- ❌ `cpa_registration` - регистрация через CPA сеть

**Email:**
- ❌ `email_newsletter_open` - открытие email рассылки
- ❌ `email_promo_click` - клик по промо email
- ❌ `email_retention` - удержание через email 


### **📋 ИНСТРУКЦИИ ДЛЯ КОМАНДЫ ПО НАСТРОЙКЕ КАНАЛОВ**

#### **🔧 1. Yandex Direct - Настройка в Adjust:**

**В Adjust Dashboard:**
1. Создать трекер: `Yandex Direct iOS` и `Yandex Direct Android`
2. Добавить макросы в URL:
   ```
   https://app.adjust.com/abc123?campaign={campaign_id}&adgroup={adgroup_id}&creative={banner_id}&utm_term={keyword}&ya_click_id={logid}
   ```
3. Включить Data Sharing → Yandex Direct
4. Настроить Postbacks для событий: install, purchase

**В Яндекс.Директ:**
1. В каждую кампанию вставить Adjust URL
2. Проверить что UTM подставляются автоматически
3. Настроить цели: установка приложения, покупка

#### **🔧 2. ASO - Настройка органического трафика:**

**В Adjust Dashboard:**
1. Создать трекер: `ASO Organic`
2. URL: `https://app.adjust.com/abc123?utm_source=app_store&utm_medium=organic`
3. Настроить Organic Attribution в настройках

**В App Store Connect:**
1. Оптимизировать keywords для поиска
2. Настроить App Store Analytics
3. Отслеживать органические установки

#### **🔧 3. Мессенджеры - Deep Links:**

**Telegram:**
1. Создать бота с Adjust ссылкой
2. URL: `https://app.adjust.com/abc123?utm_source=telegram&utm_medium=messenger`
3. Настроить Deep Links в приложении

**WhatsApp:**
1. Добавить Adjust ссылку в статус/группы
2. URL: `https://app.adjust.com/abc123?utm_source=whatsapp&utm_medium=messenger`

#### **🔧 4. CPA Сети - Postbacks:**

**Admitad:**
1. Создать трекер: `CPA Admitad`
2. URL: `https://app.adjust.com/abc123?utm_source=admitad&utm_medium=cpa`
3. Настроить Postback URL в Admitad
4. События: install, registration, purchase

**ActionPay:**
1. Аналогично Admitad
2. Настроить конверсии по событиям

#### **🔧 5. Email - UTM разметка:**

**В Email рассылках:**
1. Добавить Adjust ссылку в каждое письмо
2. URL: `https://app.adjust.com/abc123?utm_source=email&utm_medium=email&utm_campaign=newsletter_january`
3. Отслеживать открытия и клики

### **💡 Рекомендация: Расширенная система атрибуции**

```swift
// Функция для определения полного сценария атрибуции
private func determineFullAttributionScenario(attribution: ADJAttribution) -> [String: String] {
    let network = attribution.network ?? "unknown"
    let campaign = attribution.campaign ?? "unknown"
    let creative = attribution.creative ?? "unknown"
    let isFirstLaunch = attribution.isFirstLaunch ?? false
    
    var scenario: [String: String] = [:]
    
    // Базовый тип атрибуции
    if isFirstLaunch {
        scenario["attribution_type"] = "install"
        scenario["user_type"] = "new_user"
    } else {
        scenario["attribution_type"] = "reinstall"
        scenario["user_type"] = "returning_user"
    }
    
    // Источник трафика
    switch network.lowercased() {
    case "organic":
        scenario["traffic_source"] = "organic"
        scenario["attribution_type"] = isFirstLaunch ? "organic_install" : "organic_return"
    case "facebook", "fb":
        if campaign.contains("retargeting") {
            scenario["traffic_source"] = "facebook_retargeting"
            scenario["attribution_type"] = "retargeting_conversion"
        } else {
            scenario["traffic_source"] = "facebook_prospecting"
            scenario["attribution_type"] = isFirstLaunch ? "paid_install" : "prospecting_conversion"
        }
    case "google", "googleads":
        if campaign.contains("search") {
            scenario["traffic_source"] = "google_search"
        } else if campaign.contains("display") {
            scenario["traffic_source"] = "google_display"
        } else {
            scenario["traffic_source"] = "google_other"
        }
    default:
        scenario["traffic_source"] = "other_network"
    }
    
    // Стадия воронки
    if isFirstLaunch {
        if creative.contains("video") {
            scenario["funnel_stage"] = "awareness_video"
        } else if creative.contains("banner") {
            scenario["funnel_stage"] = "consideration_banner"
        } else {
            scenario["funnel_stage"] = "consideration_other"
        }
    } else {
        if campaign.contains("retargeting") {
            scenario["funnel_stage"] = "retention_retargeting"
        } else if campaign.contains("promo") {
            scenario["funnel_stage"] = "conversion_promo"
        } else {
            scenario["funnel_stage"] = "retention_other"
        }
    }
    
    return scenario
}
```

### **🚨 Что мы теряем без расширенной атрибуции:**

1. **Неточная аналитика** - не можем различать типы пользователей
2. **Плохая оптимизация** - не знаем какие каналы работают лучше
3. **Потеря ROI** - не можем точно считать эффективность кампаний
4. **Нет персонализации** - не можем адаптировать опыт под тип пользователя
5. **Сложная отчетность** - ограниченные возможности для анализа

### **🎯 Примеры сценариев, которые мы не отслеживаем:**

#### **Сценарий 1: Существующий пользователь перешел по ссылке**
```
Текущий код: "reinstall" ❌
Нужно: "returning_user_deep_link" ✅
```

#### **Сценарий 2: Ретаргетинг Facebook**
```
Текущий код: "reinstall" ❌
Нужно: "facebook_retargeting_conversion" ✅
```

#### **Сценарий 3: Органический поиск**
```
Текущий код: "install" ❌
Нужно: "organic_search_install" ✅
```

#### **Сценарий 4: Видео реклама TikTok**
```
Текущий код: "install" ❌
Нужно: "tiktok_video_awareness" ✅
```

</details>

---

*Полная инструкция подготовлено командой Rick.ai на основе официальной документации Adjust, AppMetrica, изучения лучших практик 2025 года, анализа реальных внедрений и глубокого исследования сравнения с AppsFlyer по 20+ источникам данных. Документ дополнен детальными разделами по технической архитектуре, протоколу тестирования и экономическому обоснованию.*

*Инструкция обновлена в августе 2025 года на основе официальной документации Adjust, AppMetrica, актуальных pricing data, verified industry sources, полного анализа русскоязычных каналов привлечения и comprehensive JTBD сценариев cross-platform интеграции.*

*Инструкция обновлена в январе 2025 года с критическими исправлениями Flutter кода в соответствии с официальной документацией Adjust SDK v5.4.2 и добавлением функции передачи adjust_adid в каждое событие AppMetrica.*