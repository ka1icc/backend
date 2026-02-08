# Инструкция: одна ветка — одно задание (вариант преподавателя)

## Шаг 0. Подготовка (один раз)

Открой **Git Bash** (не PowerShell). Перейди на рабочий стол и клонируй репозиторий в отдельную папку:

```bash
cd /c/Users/yulia/Desktop
git clone https://github.com/ka1icc/backend.git backend-repo
cd backend-repo
```

---

## Шаг 1. Пустая ветка с одним README

Создаём ветку **без истории** (orphan) и оставляем в ней только README:

```bash
# Ветка без истории
git checkout --orphan new-main

# Удалить из индекса всё, кроме README (папки заданий убираем)
git rm -rf 1_backend_avito-tech 2_backend_Ivelum 2>/dev/null || true
git add README.md

# Инициальный коммит
git commit -m "Initial commit: README (ФИ, группа)"
```

Если в репозитории нет папок `1_backend_avito-tech` / `2_backend_Ivelum` (уже пустой клон), то просто:

```bash
git checkout --orphan new-main
git add README.md
git commit -m "Initial commit: README (ФИ, группа)"
```

Если README в клоне другой — замени его содержимым из файла **README-FOR-BACKEND-MAIN.md** (ФИ и группа), затем:

```bash
git add README.md
git commit -m "Initial commit: README (ФИ, группа)"
```

Отправь новую ветку на GitHub:

```bash
git push origin new-main
```

---

## Шаг 2. Настройки на GitHub

1. Зайди на https://github.com/ka1icc/backend  
2. **Settings** → **General** → внизу блок **Danger Zone** не трогаем пока  
3. **Settings** → **Branches** (или **Code** → выпадающее меню веток)  
4. **Default branch** → переключи на **new-main** → **Update**  
5. Вернись в **Code**, переключись на ветку **main**  
6. Удали ветку **main** (иконка корзины рядом с веткой или в **Branches**)  
7. Переименовать **new-main** в **main**:
   - Зайди в ветку **new-main**
   - **Branches** → у **new-main** нажми **New pull request** не нужно — просто зайди в **new-main**
   - Создай ветку **main** от **new-main**: в выпадающем списке веток введи `main` и выбери **Create branch: main from new-main**
   - Снова **Settings** → **Branches** → **Default branch** → выбери **main** → **Update**
   - Удали ветку **new-main** (она уже не нужна)

В итоге: по умолчанию открывается **main**, в ней один коммит с README (ФИ и группа).

---

## Шаг 3. Ветка для задания 1 (Avito)

Локально (в папке **backend-repo**):

```bash
# Убедись, что ты на main и он обновлён
git fetch origin
git checkout main
git pull origin main

# Ветка для первого задания
git checkout -b 1-avito

# Скопировать файлы задания из папки 1_backend_avito-tech
# (выполни в PowerShell или проводнике: скопировать всё из 1_backend_avito-tech В папку backend-repo/1_backend_avito-tech)
```

В **Проводнике**: скопируй всё содержимое из  
`C:\Users\yulia\Desktop\1_backend_avito-tech`  
в  
`C:\Users\yulia\Desktop\backend-repo\1_backend_avito-tech`  
(папку `1_backend_avito-tech` создай внутри **backend-repo**, если её нет).

Вернись в Git Bash:

```bash
cd /c/Users/yulia/Desktop/backend-repo
git add 1_backend_avito-tech
git status
# Убедись, что нет лишнего (__pycache__, .db, .idea)
git commit -m "Задание 1: Avito-tech URL Shortener"
git push -u origin 1-avito
```

---

## Шаг 4. Ветка для задания 2 (Ivelum)

Когда будет готово второе задание:

```bash
git checkout main
git checkout -b 2-ivelum
# Скопировать файлы второго задания в 2_backend_Ivelum
git add 2_backend_Ivelum
git commit -m "Задание 2: Ivelum"
git push -u origin 2-ivelum
```

---

## Пулл-реквесты для преподавателя

- **Задание 1:** в репозитории на GitHub: **Compare & pull request** для ветки **1-avito** → base **main**. Преподаватель будет смотреть код и оставлять комментарии в PR.
- **Задание 2:** то же для ветки **2-ivelum** → base **main**.

Так в **main** только README, а каждое задание — в своей ветке и в отдельном PR.
