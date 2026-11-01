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
---

# Command palette (Cmd+K) — Задачи

Реализуют command palette из [спецификации](./spec.md); до раскатки всё закрыто переменной сборки `VITE_FEATURE_COMMAND_PALETTE`.

## Задачи

- [ ] **T1. Настроить окружение для компонентных тестов**
  - Покрывает: подготовка
  - Файлы: `package.json`, новый `vitest.config.ts`
  - Что сделать: добавить `jsdom` в dev-зависимости и `vitest.config.ts` с `environment: "jsdom"` (раздел «План тестирования» спецификации)
  - Готово, когда: `npx vitest run --passWithNoTests` завершается с кодом 0, а `npm run build` по-прежнему проходит
  - Зависит от: —
- [ ] **T2. Открывать и закрывать палитру по Cmd/Ctrl+K за флагом**
  - Покрывает: R1
  - Файлы: `src/hooks/useHotkey.ts`, новый `src/hooks/useHotkey.test.ts`, `src/components/layout/Header.tsx`, новый `src/components/command-palette/CommandPalette.tsx`, новый `src/components/command-palette/CommandPalette.test.tsx`, `src/analytics/track.ts`
  - Что сделать: добавить `allowInInputs` в `useHotkey`; `Header` регистрирует Cmd/Ctrl+K, только если включена `VITE_FEATURE_COMMAND_PALETTE`, хранит `open`, рендерит `CommandPalette` (`Dialog` с полем ввода) и отправляет `command_palette_opened`; добавить это событие в `EventName` (разделы «Компоненты и изменения», «API / интерфейсы»). Обработать граничные случаи хоткея: палитра уже открыта, открыт другой диалог (раздел «Граничные случаи и обработка ошибок»)
  - Готово, когда: unit-тесты показывают, что с `allowInInputs` хоткей срабатывает внутри `input`, а `?` по-прежнему нет; компонентные тесты показывают, что Cmd+K и Ctrl+K открывают палитру с фокусом в её поле, в том числе из поля ввода в фокусе, Esc закрывает её без смены URL, повторное Cmd+K не открывает второе окно, Cmd+K игнорируется, пока открыт `ShortcutsHelp`, а при выключенной переменной Cmd+K ничего не делает
  - Зависит от: T1
- [ ] **T3. Искать и открывать разделы админки**
  - Покрывает: R2, R3
  - Файлы: новый `src/components/command-palette/useSectionCommands.ts`, новый `src/components/command-palette/useSectionCommands.test.ts`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`, `src/analytics/track.ts`
  - Что сделать: `useSectionCommands` с правилом из `Sidebar` и сопоставлением `title` по подстроке; рендерить группу разделов по паттерну combobox + listbox, с ↑/↓, Enter или кликом; при выборе `navigate(path)`, закрытие и событие `command_palette_item_selected`, добавленное в `EventName`; игнорировать Enter при `e.isComposing` (разделы «Компоненты и изменения», «Граничные случаи и обработка ошибок»)
  - Готово, когда: unit-тесты показывают, что «ref» находит «Refunds» в любом регистре, без `refunds:manage` «Refunds» нет, до `loaded` нет ничего; компонентные тесты показывают, что и стрелки + Enter, и клик открывают `/refunds`, а Enter во время IME-ввода ничего не выбирает
  - Зависит от: T2
- [ ] **T4. Искать и открывать заказы и клиентов**
  - Покрывает: R4
  - Файлы: новый `src/components/command-palette/useEntitySearch.ts`, `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: `useEntitySearch` поверх `searchEntities(q, 5, signal)` от 2 символов, с debounce 150 мс, отменой устаревших запросов и отбрасыванием результатов без `orders:view` / `customers:view`; рендерить группы заказов и клиентов, их состояние ошибки и пустое состояние, когда ничего не найдено; при выборе переходить на `/orders/:orderId` или `/customers/:customerId` и дополнительно отправлять `search_result_opened` с `source: "command_palette"` (разделы «Компоненты и изменения», «API / интерфейсы», «Граничные случаи и обработка ошибок»)
  - Готово, когда: компонентные тесты с замоканным `searchEntities` показывают, что найденный заказ открывает `/orders/ORD-10482`, минуя `/search`; клиент, найденный по номеру, имени и email, открывает `/customers/CUS-2210`; запрос из 1 символа не делает вызова; результаты без `orders:view` / `customers:view` отбрасываются; при ошибке поиска разделы остаются видны и показывается состояние ошибки; если ничего не найдено, показывается пустое состояние; более медленный устаревший ответ не показывается
  - Зависит от: T3
- [ ] **T5. Запоминать недавно открытые заказы и клиентов**
  - Покрывает: R5
  - Файлы: `src/auth/usePermissions.ts`, новый `src/components/command-palette/recentItems.ts`, новый `src/components/command-palette/recentItems.test.ts`, `src/pages/OrderDetailsPage.tsx`, `src/pages/CustomerDetailsPage.tsx`
  - Что сделать: `usePermissions()` дополнительно возвращает `userId`; функции для `localStorage` и `useRecordRecent`, как в разделе «Модель данных»; вызывать `useRecordRecent` при монтировании обеих страниц деталей (раздел «Компоненты и изменения»)
  - Готово, когда: unit-тесты покрывают порядок «новые сверху», дедупликацию по типу + id, лимит в 5, отдельные ключи для каждого `userId`, сброс при невалидном JSON и отсутствие ошибки, когда `localStorage` бросает исключение
  - Зависит от: T1
- [ ] **T6. Показывать недавние пункты при пустом поле**
  - Покрывает: R5
  - Файлы: `src/components/command-palette/CommandPalette.tsx`, `src/components/command-palette/CommandPalette.test.tsx`
  - Что сделать: при пустом поле рендерить группу недавних из `recentItems` для текущего `userId`, показывая сохранённые id и скрывая пункты, к которым у агента больше нет доступа; выбор пункта ведёт на его страницу и отправляет событие с `from_recent: true` (разделы «Компоненты и изменения», «Граничные случаи и обработка ошибок»)
  - Готово, когда: компонентный тест: после того как записаны заказ A, а затем клиент B, пустая палитра показывает B, затем A, а выбор пункта открывает его страницу; заказ скрыт без `orders:view`
  - Зависит от: T4, T5
- [ ] **T7. Подставить тексты из дизайна**
  - Покрывает: подготовка
  - Файлы: `src/components/layout/ShortcutsHelp.tsx`, `src/components/command-palette/CommandPalette.tsx`
  - Что сделать: добавить пункт для Cmd/Ctrl+K в `SHORTCUTS`; подставить тексты из дизайна в пустое состояние и состояние ошибки палитры (разделы «Компоненты и изменения», «Граничные случаи и обработка ошибок»)
  - Готово, когда: справка по сочетаниям (`?`) показывает пункт для Cmd/Ctrl+K; пустое состояние и состояние ошибки показывают тексты из дизайна; существующие тесты по-прежнему проходят
  - Зависит от: T4
  - Заблокировано: дизайн (раздел PRD «Риски и зависимости»); открытого вопроса на это нет
- [ ] **T8. Включить на стейджинге и провести ручные проверки**
  - Покрывает: R1
  - Файлы: конфигурация сборки стейджинга для `VITE_FEATURE_COMMAND_PALETTE`
  - Что сделать: собрать стейджинг с включённой переменной; провести ручные проверки из раздела «План тестирования»
  - Готово, когда: на macOS и Windows, в браузерах, которыми пользуется поддержка, Cmd/Ctrl+K открывает палитру, а собственное Ctrl+K / Cmd+K браузера не срабатывает
  - Зависит от: T6, T7
- [ ] **T9. Включить в проде**
  - Покрывает: подготовка
  - Файлы: конфигурация сборки прода для `VITE_FEATURE_COMMAND_PALETTE`
  - Что сделать: собрать и задеплоить прод с переменной, включённой для всех; откат — пересборка с выключенной переменной (раздел «Раскатка и откат»)
  - Готово, когда: в проде Cmd/Ctrl+K открывает палитру, а события `command_palette_opened` и `command_palette_item_selected` приходят в аналитику
  - Зависит от: T8
  - Заблокировано: Spec Q3, PRD Q2
