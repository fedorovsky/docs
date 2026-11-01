---
type: tasks
title: Command palette (Cmd+K)
feature: command-palette
lang: ru
mirror: ../en/tasks.md
status: draft
owner: TBD
created: 2026-11-01
updated: 2026-11-01
prd: ./prd.md
spec: ./spec.md
links: [ADMIN-231]
---

# Command palette (Cmd+K) — Задачи

Реализуют клиентскую командную палитру из [спецификации](./spec.md); до раскатки всё закрыто переменной сборки `VITE_FEATURE_COMMAND_PALETTE`.

## Задачи

- [ ] **T1. Настроить Vitest с jsdom**
  - Покрывает: `setup`
  - Файлы: `package.json`, `vitest.config.ts`, `src/components/ui/Dialog.test.tsx`
  - Что сделать: добавить `jsdom` в dev-зависимости и `vitest.config.ts` с окружением `jsdom` (раздел «План тестирования» спецификации)
  - Готово, когда: `npx vitest run` проходит smoke-тест, который рендерит открытый `Dialog` и находит его заголовок
  - Зависит от: —
- [ ] **T2. Добавить в `useHotkey` опцию `allowInInputs`**
  - Покрывает: R1
  - Файлы: `src/hooks/useHotkey.ts`, `src/hooks/useHotkey.test.ts`
  - Что сделать: новая опция `allowInInputs` (по умолчанию `false`), которая отключает проверку фокуса в поле ввода (разделы «Компоненты и изменения», «API / интерфейсы»)
  - Готово, когда: проходят тесты: с `{ meta: true, allowInInputs: true }` обработчик срабатывает на Cmd+K и Ctrl+K, в том числе из `input` в фокусе; `?` без опции по-прежнему игнорируется в `input`
  - Зависит от: T1
- [ ] **T3. Открывать и закрывать палитру из хедера, за флагом**
  - Покрывает: R1
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/layout/Header.tsx`, `src/components/layout/Header.test.tsx`
  - Что сделать: каркас `CommandPalette` (`Dialog` + поле ввода, временные тексты); `Header` регистрирует Cmd/Ctrl+K и хранит `open`, только если включён `VITE_FEATURE_COMMAND_PALETTE` (разделы «Компоненты и изменения», «Раскатка и откат»)
  - Готово, когда: проходят тесты: при включённом флаге Cmd+K и Ctrl+K открывают палитру с фокусом в её поле ввода, в том числе из поиска в хедере; Esc закрывает её; Cmd+K при открытой палитре оставляет одно окно; при открытом `ShortcutsHelp` сочетание игнорируется; при выключенном флаге ничего не открывается
  - Зависит от: T2
- [ ] **T4. Добавить `useSectionCommands`**
  - Покрывает: R2, R3
  - Файлы: `src/components/command-palette/useSectionCommands.ts`, `src/components/command-palette/useSectionCommands.test.ts`
  - Что сделать: фильтровать `routes` по `inNav && has(permission)` и сопоставлять `title` по подстроке без учёта регистра; ничего не возвращать, пока нет `loaded` (раздел «Компоненты и изменения»)
  - Готово, когда: проходят тесты: «ref» возвращает Refunds при `refunds:manage` и ничего без него; страницы деталей и `/search` не попадают никогда; пока `loaded` равно `false`, результат пустой
  - Зависит от: T1
- [ ] **T5. Показывать разделы в палитре и открывать выбранный**
  - Покрывает: R2, R3
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: группа разделов из `useSectionCommands`; ↑/↓, Enter или клик вызывают `navigate(path)` и закрывают палитру; ARIA combobox + listbox; Enter игнорируется при `e.isComposing` (разделы «Компоненты и изменения», «Граничные случаи»)
  - Готово, когда: проходят тесты: ввод «ref», затем ↓ + Enter или клик открывают `/refunds` и закрывают палитру; `aria-activedescendant` следует за активным пунктом; Enter во время IME-ввода ничего не выбирает
  - Зависит от: T3, T4
- [ ] **T6. Добавить `useEntitySearch`**
  - Покрывает: R4
  - Файлы: `src/components/command-palette/useEntitySearch.ts`, `src/components/command-palette/useEntitySearch.test.ts`
  - Что сделать: TanStack Query поверх `searchEntities(q, 5, signal)`, debounce 150 мс, включается от 2 символов; отбрасывать результаты без `orders:view` / `customers:view` (раздел «Компоненты и изменения», допущение PRD Q4)
  - Готово, когда: проходят тесты с замоканным `searchEntities`: при длине меньше 2 символов вызова нет; после паузы 150 мс ровно один вызов; `signal` устаревшего запроса отменяется; без каждого из прав соответствующие результаты отбрасываются
  - Зависит от: T1
- [ ] **T7. Показывать заказы и клиентов в палитре**
  - Покрывает: R4
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: группы заказов и клиентов из `useEntitySearch`; выбор ведёт на `/orders/:orderId` или `/customers/:customerId`; состояния ошибки и пустого результата с временными текстами (раздел «Граничные случаи»)
  - Готово, когда: проходят тесты: номер заказа показывает заказ, и Enter открывает `/orders/<id>` без захода на `/search`; то же для клиента, найденного по номеру, имени и email; при ошибке поиска разделы остаются и показывается состояние ошибки; без совпадений показывается пустое состояние
  - Зависит от: T5, T6
- [ ] **T8. Сохранять недавно открытые заказы и клиентов**
  - Покрывает: R5
  - Файлы: `src/auth/usePermissions.ts`, `src/components/command-palette/recentItems.ts`, `src/components/command-palette/recentItems.test.ts`, `src/pages/OrderDetailsPage.tsx`, `src/pages/CustomerDetailsPage.tsx`
  - Что сделать: `usePermissions()` дополнительно возвращает `userId`; функции `recentItems` и `useRecordRecent` поверх `acme-admin:recent:<userId>`, их вызывают при монтировании обе страницы деталей (раздел «Модель данных», допущения PRD Q5, PRD Q6)
  - Готово, когда: проходят тесты: новые первыми, дедупликация по type + id, не больше 5, отдельные ключи для каждого пользователя, невалидный JSON сбрасывает значение; монтирование страницы деталей записывает её id
  - Зависит от: T1
- [ ] **T9. Показывать недавние при пустом поле ввода**
  - Покрывает: R5
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: группа недавних с сохранёнными id при пустом поле; скрывать пункты, на которые у агента больше нет прав; выбор открывает страницу (разделы «Модель данных», «Граничные случаи»)
  - Готово, когда: проходят тесты: после открытия заказа A, а затем клиента B палитра показывает B, A; выбор пункта открывает его страницу; пункт без прав скрыт; если `localStorage` бросает ошибку, остальная палитра работает
  - Зависит от: T7, T8
- [ ] **T10. Отправлять события аналитики палитры**
  - Покрывает: `setup`
  - Файлы: `src/analytics/track.ts`, `src/components/layout/Header.tsx`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: добавить `command_palette_opened` / `command_palette_item_selected` в `EventName` и отправлять их; для заказов и клиентов отправлять `search_result_opened` с `source: "command_palette"` (раздел «API / интерфейсы»)
  - Готово, когда: проходят тесты с замоканным `track`: открытие отправляет `{ trigger: "hotkey" }`; выбор заказа отправляет `command_palette_item_selected` с `kind`, `from_recent`, `query_length`, `ms_since_open` и `search_result_opened` с `source: "command_palette"`
  - Зависит от: T9
- [ ] **T11. Применить тексты из дизайна и пункт в справке по сочетаниям**
  - Покрывает: R1, R2, R4, R5
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/layout/ShortcutsHelp.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: заменить временные тексты текстами из дизайна; добавить пункт Cmd/Ctrl+K в `SHORTCUTS` (раздел «Компоненты и изменения»)
  - Готово, когда: палитра и справка по сочетаниям совпадают с макетами; `npx vitest run` проходит
  - Зависит от: T10
  - Заблокировано: PRD Q12
- [ ] **T12. Включить на стейджинге и проверить на macOS и Windows**
  - Покрывает: `verify`
  - Файлы: окружение сборки стейджинга (конфиг деплоя): `VITE_FEATURE_COMMAND_PALETTE`
  - Что сделать: собрать стейджинг с включённой переменной и пройти ручные проверки из раздела «План тестирования»
  - Готово, когда: на macOS и Windows в браузерах, которыми пользуется поддержка, проходят критерии приёмки R1–R5 из PRD, а собственное Cmd+K / Ctrl+K браузера не срабатывает
  - Зависит от: T11
- [ ] **T13. Раскатить в прод**
  - Покрывает: `rollout`
  - Файлы: окружение сборки прода (конфиг деплоя): `VITE_FEATURE_COMMAND_PALETTE`
  - Что сделать: собрать и задеплоить прод с включённой переменной для всех; откат — пересборка с выключенной (раздел «Раскатка и откат»)
  - Готово, когда: агенты в проде открывают палитру, и события `command_palette_opened` приходят с прода
  - Зависит от: T12
  - Заблокировано: Spec Q3, PRD Q2
