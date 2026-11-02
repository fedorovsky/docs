---
type: spec
title: Identity пользователя и согласие на трекинг
feature: identity-tracking-consent
lang: ru
mirror: ../en/spec.md
status: draft
owner: TBD
reviewers: []
created: 2026-11-02
updated: 2026-11-02
prd: ./prd.md
links: [TRACK-12]
---

# Identity пользователя и согласие на трекинг — Спецификация

## Кратко

Сервис identity загружает стартовый конфиг через `IdentityApi`, кладёт семь полей identity в обсервер identity и сохраняет согласие через тот же API; обсервер вызывает трёх запоминающих подписчиков (хедеры запросов, коллектор аналитики, гейм-конфиг) при старте и при каждом изменении поля. Пока бэкенд не готов, `IdentityApi` — фейк, который хранит выбор в `localStorage` и отвечает с задержкой и периодическими ошибками. UI — одна страница с двумя блоками согласия и тремя блоками мониторинга. Зачем это нужно, описано в [PRD](./prd.md).

## Контекст и текущее состояние

- Проект `playground/app/` пуст: нет `package.json`, нет исходников. README playground описывает его как фронтенд на React + TypeScript, поэтому первая задача создаёт каркас приложения Vite + React + TypeScript с Vitest; все пути ниже новые и указаны относительно `playground/app/`.
- Бэкенда нет. Методы конфига и согласия в работе, согласованный контракт к тикету не приложен (Spec Q1); фейк реализует имена полей из TRACK-12 и форматы из раздела «API / интерфейсы».
- В приложении нет HTTP-клиента, коллектора аналитики и гейм-конфига, поэтому три подписчика запоминают, что получили, вместо вызова реальных систем.

## Предлагаемое решение

### Обзор

```mermaid
sequenceDiagram
  participant Main as main.tsx
  participant Service as identityService
  participant Api as fakeIdentityApi
  participant Storage as localStorage
  participant Observer as identityObserver
  participant Subs as subscribers
  Main->>Observer: subscribe(requestHeaders, analyticsCollector, gameConfig)
  Main->>Service: start()
  Service->>Api: getConfig()
  Api->>Storage: читает сохранённый выбор
  Api-->>Service: IdentityFields
  Service->>Observer: set(fields)
  Observer->>Subs: вызывает каждого со всеми полями
  Note over Service: пользователь нажимает Save или Accept all
  Service->>Api: updateConsent(request)
  Api->>Storage: пишет новый выбор
  Api-->>Service: ConsentResponse
  Service->>Observer: set(fields)
  Observer->>Subs: вызывает каждого, только если поле изменилось
```

### Компоненты и изменения

- `src/identity/types.ts` — новый: `ConsentStatus` (`Declined = 0`, `Accepted = 1`, `NotDecided = 2`), `IdentityFields` (семь полей конфига), `ConsentRequest`, `ConsentResponse`.
- `src/identity/identityObserver.ts` — новый: `createIdentityObserver()` с `set(fields)`, `get()`, `subscribe(fn)`. `set` сохраняет поля и вызывает каждого подписчика, если это первый set или любое из семи полей отличается (строгое равенство по полю); иначе ничего не делает. Подписчик, добавленный после первого `set`, сразу вызывается с текущими полями. `subscribe` и `get` также обслуживают React через `useSyncExternalStore`.
- `src/identity/useIdentity.ts` — новый: `useIdentity(observer)`, хук `useSyncExternalStore`, которым пользуются оба блока согласия.
- `src/identity/identityService.ts` — новый: `createIdentityService(api, observer)` со `start()` (вызывает `getConfig`, затем `observer.set`) и `saveConsent(request)` (вызывает `updateConsent`; при успехе сливает два статуса из запроса и два ID из ответа в текущие поля и вызывает `observer.set`; при ошибке пробрасывает её и ничего не трогает).
- `src/api/identityApi.ts` — новый: интерфейс `IdentityApi`; адаптер настоящего бэкенда реализует его позже.
- `src/api/fakeIdentityApi.ts` — новый: `createFakeIdentityApi(options)`; поведение в разделах «Модель данных» и «API / интерфейсы».
- `src/subscribers/recorder.ts` — новый: `createRecorder(project)` оборачивает проекцию `(fields) => state` в подписчика, который хранит спроецированное состояние с `updatedAt` и отдаёт `getSnapshot()` / `subscribe(fn)` для UI мониторинга.
- `src/subscribers/requestHeaders.ts`, `src/subscribers/analyticsCollector.ts`, `src/subscribers/gameConfig.ts` — новые: три проекции из раздела «Поля подписчиков».
- `src/ui/ConsentBlock.tsx` — новый: один компонент для обоих блоков (`variant: 'initial' | 'settings'`); два переключателя, "Save", "Accept all", состояния ожидания и ошибки.
- `src/ui/MonitoringBlock.tsx` — новый: состояние рекордера в виде форматированного JSON плюс время обновления.
- `src/ui/StartPanel.tsx` — новый: отладочная панель старта наверху страницы: переключатель `consentRequired` (по умолчанию включён) и кнопка "Start", отключённая, пока старт выполняется.
- `src/ui/ConfigBlock.tsx` — новый: текущие семь полей обсервера в виде форматированного JSON, наверху страницы.
- `src/App.tsx` — страница: панель старта; по "Start" создаёт API через `createApi(consentRequired)` и новый `identityService`, вызывает `start()` и держит его состояния ожидания и ошибки; как только у обсервера есть поля, показывает блок конфига, два блока согласия по правилам видимости и три блока мониторинга.
- `src/main.tsx` — сборка: создаёт обсервер и три рекордера, подписывает рекордеры и рендерит `App` с `createApi = (consentRequired) => createFakeIdentityApi({ consentRequired })`.

#### Поля подписчиков

| Поле | Все три подписчика | Только хедеры запросов |
|------|--------------------|------------------------|
| `marketingTrackingId`, `analyticsTrackingId`, `temporaryId` | всегда | |
| `deviceId` | только при `consentRequired = false` | |
| `marketingConsentStatus`, `analyticsConsentStatus` | только при `consentRequired = true` | |
| `consentRequired` | | всегда |

Обсервер по-прежнему доставляет все семь полей; проекция отбрасывает `deviceId` при `consentRequired = true`, так что он никогда не попадает в состояние рекордера. Хедеры запросов — строки (статусы как `"0"` / `"1"` / `"2"`, `consentRequired` как `"true"` / `"false"`), а хедер, значение которого было бы `null`, не добавляется. Коллектор аналитики и гейм-конфиг сохраняют значения `null`.

Имена хедеров (Spec Q3): `X-Marketing-Tracking-Id`, `X-Analytics-Tracking-Id`, `X-Temporary-Id`, `X-Device-Id`, `X-Marketing-Consent-Status`, `X-Analytics-Consent-Status`, `X-Consent-Required`.

#### Видимость и поведение UI

- Стартовый блок: `consentRequired === true` и хотя бы один статус `NotDecided`. Блок настроек: `consentRequired === true`. До нажатия "Start", а также пока первый `start()` выполняется или упал, показывается только панель старта.
- Переключатель включён при `Accepted` и выключен при `Declined`. **Допущение (PRD Q2):** `NotDecided` показывается как выключенный.
- "Save" отправляет `{ marketing: on ? Accepted : Declined, analytics: … }`; "Accept all" отправляет оба как `Accepted` независимо от переключателей. Оба блока читают статусы из обсервера, поэтому сохранение в одном обновляет другой. После успешного сохранения переключатели выставляются по отправленному запросу, поэтому "Accept all" или сохранение после упавшего не рассинхронизирует их со статусом, который не изменился.
- **Допущение (PRD Q3):** пока вызов выполняется, обе кнопки отключены; при ошибке блок показывает "Could not save your choice. Try again." под кнопками и оставляет переключатели как их выставил пользователь; упавший `start()` показывает "Could not load the config." с кнопкой "Retry", которая снова вызывает `start()`.
- **Допущение (PRD Q4):** временные английские тексты: заголовки блоков "Tracking consent" и "Tracking settings", подписи переключателей "Marketing" и "Analytics", кнопки "Save" и "Accept all", заголовки мониторинга "Config", "Request headers", "Analytics collector" и "Game config". Поздняя задача заменяет их окончательным дизайном.

### Модель данных

Жизненный цикл статуса одного согласия; второе независимо:

```mermaid
stateDiagram-v2
  [*] --> NotDecided: consentRequired = true, first start
  [*] --> Accepted: consentRequired = false
  NotDecided --> Accepted: сохранён включённым, новый ID
  NotDecided --> Declined: сохранён выключенным, ID сброшен
  Accepted --> Accepted: сохранён включённым, тот же ID
  Accepted --> Declined: сохранён выключенным, ID сброшен
  Declined --> Accepted: сохранён включённым, новый ID
  Declined --> Declined: сохранён выключенным, ID сброшен
```

Хранилище фейка: ключ `localStorage` `track12.identity` содержит `{ marketingConsentStatus, analyticsConsentStatus, marketingTrackingId, analyticsTrackingId }`. `deviceId` — константа `"device-0001"`; `temporaryId` — `crypto.randomUUID()` при каждом `getConfig`; tracking ID — `crypto.randomUUID()` при выдаче.

### API / интерфейсы

```ts
interface IdentityApi {
  getConfig(): Promise<IdentityFields>;
  updateConsent(request: ConsentRequest): Promise<ConsentResponse>;
}

interface IdentityFields {
  marketingTrackingId: string | null;
  analyticsTrackingId: string | null;
  deviceId: string;
  temporaryId: string;
  consentRequired: boolean;
  marketingConsentStatus: ConsentStatus;
  analyticsConsentStatus: ConsentStatus;
}

interface ConsentRequest { marketing: ConsentStatus; analytics: ConsentStatus } // Accepted or Declined
interface ConsentResponse { marketingTrackingId: string | null; analyticsTrackingId: string | null }
```

Поведение фейка, `createFakeIdentityApi({ consentRequired, delayMs = [300, 1000], errorRate = 0.1, random = Math.random, storage = localStorage })`:

- Каждый вызов ждёт случайную задержку из `delayMs`. `updateConsent` затем с вероятностью `errorRate` падает (`Error("Fake backend error")`) до обращения к хранилищу; `getConfig` пока не падает никогда (PRD R11).
- `getConfig` при `consentRequired = true`: статусы и ID из хранилища или `NotDecided` / `null`, если ничего не сохранено.
- `getConfig` при `consentRequired = false`: оба статуса `Accepted`; ID из хранилища, если есть, иначе выдаются и сохраняются; сохранённые статусы игнорируются.
- `updateConsent`, по каждому полю: `Accepted` при сохранённом статусе `Accepted` → тот же ID; `Accepted` в остальных случаях → новый ID; `Declined` → `null`. Оба статуса и оба ID сохраняются вместе после проверки на ошибку, поэтому упавший вызов ничего не меняет.

`consentRequired` для фейка — это переключатель панели старта; больше фейк его ниоткуда не читает.

## Покрытие требований

| ID в PRD | Как выполняется | Раздел |
|----------|-----------------|--------|
| R1 | Фейковый `getConfig` возвращает семь полей; `temporaryId` новый при каждом вызове, `deviceId` константа | API / интерфейсы |
| R2 | Фейк возвращает `Accepted` и ID при `consentRequired = false`; `App` скрывает оба блока | API / интерфейсы, Видимость и поведение UI |
| R3 | `ConsentBlock` с вариантом `initial`, показан по правилу видимости | Видимость и поведение UI |
| R4 | `ConsentBlock` с вариантом `settings`; выключенный переключатель + "Save" отправляет `Declined` | Видимость и поведение UI |
| R5 | Один вызов `updateConsent` с обоими полями; "Accept all" отправляет оба `Accepted` | Видимость и поведение UI, API / интерфейсы |
| R6 | Правила ID в фейковом `updateConsent` | API / интерфейсы, Модель данных |
| R7 | Фейк падает до сохранения; сервис пробрасывает ошибку без `observer.set`; блок показывает ошибку | Компоненты и изменения, Граничные случаи и обработка ошибок |
| R8 | `identityObserver.set` вызывает подписчиков при первом set и только если поле изменилось | Компоненты и изменения |
| R9 | Три проекции из раздела «Поля подписчиков» | Поля подписчиков |
| R10 | `ConfigBlock` на обсервере и `MonitoringBlock` на каждый рекордер, перерисовываются через `useSyncExternalStore` | Компоненты и изменения |
| R11 | Фейк с задержкой, `errorRate` и `localStorage` | API / интерфейсы |
| R12 | `StartPanel` и обработка старта в `App`: новые фейковый API и сервис на каждый "Start" | Компоненты и изменения |

## Альтернативы и решения

| Решение | Рассмотренные варианты | Выбрано | Почему |
|---------|------------------------|---------|--------|
| Откуда UI читает identity | Отдельное состояние React, скопированное из сервиса; обсервер как стор через `useSyncExternalStore` | Обсервер как стор | Один источник истины; оба блока и мониторинг обновляются вместе с подписчиками |
| Статусы согласия после сохранения | Из ответа; из запроса | Из запроса | По тикету метод согласия возвращает только два tracking ID; статус по определению следует за запросом |
| Хранение в фейке | Только в памяти; `localStorage` | `localStorage` | Тикет требует, чтобы выбор переживал перезагрузку |
| Переключение `consentRequired` в фейке | Константа на этапе сборки; query-строка URL `?consentRequired=false`; переключатель на отладочной панели старта | Переключатель панели старта, по умолчанию включён | Тестировщики переключают режимы и перезапускают без перезагрузки; значение по-прежнему приходит только из объекта конфига |
| Задержка и доля ошибок фейка | Фиксированные значения; опции со значениями по умолчанию 300–1000 мс и 10% | Опции со значениями по умолчанию; ошибки только в `updateConsent` | Тесты идут без задержки и ошибок; ручное тестирование видит задержки и упавшие сохранения, а старт не падает никогда (PRD R11) |
| Отбрасывание `deviceId` | В обсервере; в проекции каждого подписчика | Проекция | По тикету обсервер доставляет все семь полей; правило касается того, что пишут подписчики |
| Имена хедеров | Тикет оставляет их на усмотрение инженера | Имена `X-…` из раздела «Поля подписчиков» | Общепринятые; подтверждаются с бэкендом до настоящей интеграции (Spec Q3) |

## Граничные случаи и обработка ошибок

- `start()` падает (фейк здесь не падает никогда; настоящий бэкенд может) → страница показывает "Could not load the config." и "Retry"; ни один подписчик не вызывается; "Retry" запускает снова с текущим значением переключателя.
- "Start" нажат, пока старт выполняется → невозможно, кнопка отключена.
- "Start" нажат снова после успешного старта → новые фейковый API и сервис; обсервер получает новый конфиг (как минимум новый `temporaryId`), поэтому подписчики вызываются; упавший перезапуск оставляет на странице прежнее состояние и показывает ошибку.
- Сохранение падает → сервис отклоняет промис, обсервер не тронут, блок показывает ошибку и оставляет переключатели как их выставил пользователь; "Save" и "Accept all" снова включены.
- Сохранение без изменений (оба уже `Accepted`, оба переключателя включены) → фейк возвращает те же ID, `observer.set` не видит изменений, ни один подписчик не вызывается, время в мониторинге не меняется.
- Оба согласия `Declined`, оба переключателя выключены, "Save" → оба остаются `Declined` с `null` ID; изменений нет, подписчики не вызываются.
- Второй клик, пока вызов выполняется → невозможен, кнопки отключены.
- Сохранение в одном блоке → оба блока заново читают статусы из обсервера; стартовый блок исчезает, как только оба решены.
- Перезагрузка после принятия → `getConfig` возвращает сохранённые `Accepted` и те же ID; новый `temporaryId` означает, что подписчики вызываются при старте.
- `consentRequired = false` при сохранённом с прошлого запуска выборе `Declined` → статусы `Accepted`, ID выдаются там, где их нет.
- `localStorage` недоступен или испорчен → фейк ведёт себя так, будто ничего не сохранено, и держит выбор в памяти на время сессии.
- Подписчик добавлен после завершения `start()` → сразу вызывается с текущими полями.
- `start()` вызван, пока старт ещё выполняется (React StrictMode в разработке монтирует дважды) → второй вызов делит запрос с первым; один `getConfig`, один `temporaryId`, один вызов подписчиков.

## Нефункциональные требования

- Приватность: при `consentRequired = true` `deviceId` никогда не появляется в состоянии рекордера и в блоках мониторинга (R9). Ничего не покидает браузер: запросы не отправляются.

## План тестирования

- Unit (Vitest): `identityObserver` (первый set вызывает, изменённое поле вызывает, идентичный set не вызывает, поздний подписчик вызывается); `fakeIdentityApi` (первый старт, `consentRequired = false`, правила ID из R6, атомарный сбой, сохранение через фейковое хранилище); `identityService` (пути старта и сохранения, сбой не трогает обсервер); три проекции (оба режима `consentRequired`, хедер с `null` отброшен, `null` сохранён в остальных).
- Компонентные (Vitest + Testing Library): `ConsentBlock` (видимость по варианту, выключенный переключатель сохраняет `Declined`, "Accept all", отключение на время ожидания, текст ошибки с сохранёнными переключателями; R3–R5, R7); `MonitoringBlock` (обновление состояния и времени) и `ConfigBlock` (все семь полей, перерисовка при изменении; R10).
- Компонентные (Vitest + Testing Library): `App` (до "Start" только панель старта, старт в обоих режимах, перезапуск в другом режиме, упавший старт с "Retry"; R12).
- Ручные, в браузере, в обоих режимах: критерии приёмки R1–R11 из PRD, включая упавшее сохранение, цикл «отозвать и принять» и перезагрузку.

## Раскатка и откат

Раскатка — это сам релиз: один деплой фронтенда, без миграций и изменений бэкенда. Блоки согласия и мониторинга рендерит `App.tsx` после "Start" на отладочной панели старта, которая собирается в последней задаче, нужной флоу, так что недостроенный UI недоступен. Откат: задеплоить предыдущую версию; ключ `track12.identity` остаётся в `localStorage` неиспользуемым и читается снова при следующей раскатке. Где деплоится приложение, неизвестно (Spec Q2).

## Открытые вопросы

- [ ] **Q1.** Согласованный контракт бэкенда к тикету не приложен: совпадают ли имена полей, коды статусов и формат метода согласия с разделом «API / интерфейсы»? — команда бэкенда
- [ ] **Q2.** Где и как деплоится приложение? В репозитории нет пайплайна. — TBD
- [ ] **Q3.** Подходят ли бэкенду имена хедеров из раздела «Поля подписчиков»? — команда бэкенда
