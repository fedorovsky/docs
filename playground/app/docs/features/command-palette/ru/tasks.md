---
type: tasks
title: Командная палитра (Cmd+K)
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

# Командная палитра (Cmd+K) — Задачи

Реализуют командную палитру из [спецификации](./spec.md); до раскатки всё за флагом `VITE_FF_COMMAND_PALETTE`. Спецификация в статусе `draft`, поэтому задачи могут меняться вместе с ней.

## Задачи

- [ ] **T1. Добавить фича-флаг**
  - Покрывает: `setup`
  - Файлы: `src/flags.ts`, конфиг окружений для `VITE_FF_COMMAND_PALETTE`
  - Что сделать: `isEnabled("command_palette")`, читающий `import.meta.env.VITE_FF_COMMAND_PALETTE` (раздел «Компоненты и изменения»); по умолчанию выключен
  - Готово, когда: `npm run build` проходит, и `isEnabled("command_palette")` возвращает `false` без переменной
  - Зависит от: —
- [ ] **T2. Научить `useHotkey` срабатывать внутри текстовых полей**
  - Покрывает: R1
  - Файлы: `src/hooks/useHotkey.ts`, `src/hooks/useHotkey.test.ts`
  - Что сделать: добавить опцию `inInputs`, которая пропускает проверку на `input` / `textarea` / `contenteditable` (раздел «Компоненты и изменения»)
  - Готово, когда: тесты показывают, что обработчик срабатывает при фокусе в поле ввода с `inInputs: true` и не срабатывает без неё; `?` по-прежнему игнорируется внутри полей
  - Зависит от: —
- [ ] **T3. Добавить `matchSections`**
  - Покрывает: R2, R4
  - Файлы: `src/components/palette/matchSections.ts`, `src/components/palette/matchSections.test.ts`
  - Что сделать: чистая функция по `routes` с `inNav && has(permission)` и поиском по `title` без учёта регистра (раздел «Компоненты и изменения»)
  - Готово, когда: тесты: «ref» возвращает «Refunds»; роут без прав исключён при любом запросе; роуты с `inNav: false` исключены; пустой запрос возвращает все разрешённые
  - Зависит от: —
- [ ] **T4. Добавить `useRecentItems`**
  - Покрывает: R5
  - Файлы: `src/components/palette/useRecentItems.ts`, `src/components/palette/useRecentItems.test.ts`
  - Что сделать: список в `localStorage` по user id с upsert в начало, сохранением label, лимитом 10, фильтром по правам и `useRecordVisits()` (разделы «Компоненты и изменения», «Модель данных»)
  - Готово, когда: тесты покрывают порядок при upsert, сохранение label, лимит, ключ по пользователю, повреждённый JSON → пустой список, фильтрацию через `has()`
  - Зависит от: —
- [ ] **T5. Собрать палитру с разделами и навигацией с клавиатуры**
  - Покрывает: R1, R2, R4, R6
  - Файлы: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`, `src/components/layout/AppLayout.tsx`
  - Что сделать: диалог Radix с полем ввода, группа "Sections" из `matchSections`, Up / Down / Enter, хоткей `{ meta: true, inInputs: true }`; монтируется в `AppLayout` при включённом флаге (раздел «Компоненты и изменения»)
  - Готово, когда: при включённом флаге Cmd+K и Ctrl+K открывают палитру, в том числе из поиска в хедере; «ref» и Enter открывают `/refunds`; без `refunds:manage` «Refunds» отсутствует; при выключенном флаге ничего не рендерится; тесты проходят
  - Зависит от: T1, T2, T3
- [ ] **T6. Добавить в палитру поиск заказов и клиентов**
  - Покрывает: R3, R4
  - Файлы: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`
  - Что сделать: дебаунснутый `searchEntities(q, 10)` начиная с 2 символов, группы "Orders" / "Customers" с фильтром по правам, состояния "Searching…", "Search is unavailable" и "No results for “<query>”" (раздел «Граничные случаи»)
  - Готово, когда: тесты с замоканным `searchEntities`: результаты сгруппированы, Enter открывает `/orders/<id>`; запроса нет при меньше чем 2 символах или без обоих прав на просмотр; состояние ошибки показывается
  - Зависит от: T5
- [ ] **T7. Показывать и записывать недавние элементы**
  - Покрывает: R5
  - Файлы: `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`, `src/pages/SearchPage.tsx`
  - Что сделать: группа "Recent" при пустом запросе; `record()` при выборе в палитре и при клике по результату в `SearchPage`; `useRecordVisits()` в палитре (раздел «Компоненты и изменения»)
  - Готово, когда: открыть два заказа, нажать Cmd+K: оба в списке, последний первым, выбор одного открывает его; тесты проходят
  - Зависит от: T4, T6
- [ ] **T8. Добавить события аналитики палитры**
  - Покрывает: `setup`
  - Файлы: `src/analytics/track.ts`, `src/components/palette/CommandPalette.tsx`, `src/components/palette/CommandPalette.test.tsx`
  - Что сделать: добавить `command_palette_opened` и `command_palette_item_opened` со свойствами из раздела «API / интерфейсы»
  - Готово, когда: тест проверяет оба события с `kind`, `position`, `query_length`, `duration_ms`; оба видны в отладчике аналитики локально
  - Зависит от: T7
- [ ] **T9. Добавить шорткат в справку по клавиатурным сокращениям**
  - Покрывает: R7
  - Файлы: `src/components/layout/ShortcutsHelp.tsx`
  - Что сделать: добавить запись «Cmd+K / Ctrl+K» — «Open command palette» при включённом флаге (раздел «Компоненты и изменения»)
  - Готово, когда: при включённом флаге «?» показывает запись; при выключенном её нет
  - Зависит от: T1
- [ ] **T10. Применить финальный дизайн и тексты**
  - Покрывает: R2, R3, R5
  - Файлы: `src/components/palette/CommandPalette.tsx`, файл стилей приложения для классов `palette-*`
  - Что сделать: заменить временную раскладку и тексты на макеты (раздел «Компоненты и изменения», стили)
  - Готово, когда: палитра на стейджинге соответствует макетам, и все тесты палитры по-прежнему проходят
  - Зависит от: T7, T9
  - Заблокировано: PRD Q4
- [ ] **T11. Проверить на стейджинге**
  - Покрывает: `verify`
  - Файлы: конфиг стейджинга для `VITE_FF_COMMAND_PALETTE`
  - Что сделать: пройти ручные проверки из раздела «План тестирования» с двумя аккаунтами с разными правами, на macOS и Windows
  - Готово, когда: критерии приёмки R1–R7 проходят на стейджинге для обоих аккаунтов
  - Зависит от: T8, T9
- [ ] **T12. Раскатить**
  - Покрывает: `rollout`
  - Файлы: конфиг продакшена для `VITE_FF_COMMAND_PALETTE`
  - Что сделать: включить флаг в продакшене (раздел «Раскатка и откат»)
  - Готово, когда: флаг включён в продакшене неделю, и события `command_palette_item_opened` поступают
  - Зависит от: T10, T11
