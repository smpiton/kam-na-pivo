# Kam na pivo

Друзья ставят на карту Праги точки, где им удобно встретиться, с радиусом и весом от 1 до 10.
Страница показывает зону пересечения и десятку пивных (данные OpenStreetMap), куда удобнее всего пойти.
Каждая встреча живёт по своей ссылке вида `…/#r-abc123`.

## Файлы

- `index.html`: готовая страница для GitHub Pages (собирается из `src/`)
- `firebase-config.js`: ключи Firebase, их нужно вставить один раз
- `firestore.rules`: правила базы: читать могут все, а писать только свои точки
- `kam-na-pivo.html`: версия для Claude Artifact
- `src/template.html`, `src/build.py`: исходник и сборка

## Настройка Firebase (один раз, ~10 минут)

1. Открой <https://console.firebase.google.com>, нажми **Create a project** и придумай любое имя. Google Analytics можно выключить.
2. **Build → Authentication → Get started → Sign-in method → Anonymous → Enable**.
3. **Build → Firestore Database → Create database**: регион `eur3 (europe-west)`, режим **production**.
4. В Firestore открой вкладку **Rules**, вставь содержимое `firestore.rules` и нажми **Publish**.
5. **Project settings** (шестерёнка) → **Your apps** → иконка `</>` (Web) → любое имя → **Register app**.
   Скопируй значения из `firebaseConfig` в `firebase-config.js`.
6. **Authentication → Settings → Authorized domains → Add domain**: `smpiton.github.io`.

Ключи в `firebase-config.js` не секретные: доступ защищают правила из шага 4.

## Публикация на GitHub Pages

1. На GitHub создай пустой публичный репозиторий `kam-na-pivo` (без README).
2. В этой папке выполни:

   ```bash
   git remote add origin https://github.com/smpiton/kam-na-pivo.git
   git push -u origin main
   ```

3. В репозитории открой **Settings → Pages → Source: Deploy from a branch → main / (root) → Save**.
4. Через минуту сайт заработает по адресу `https://smpiton.github.io/kam-na-pivo/`.
   При первом открытии страница сама создаст ссылку на встречу. Скопируй её и отправь друзьям.

## Пересборка

```bash
python3 src/build.py <osm_dir> <leaflet.css> index.html github
python3 src/build.py <osm_dir> <leaflet.css> kam-na-pivo.html claude
```

`osm_dir` содержит `pubs.json` и `geo.json` из Overpass API, а `leaflet.css` берётся из cdnjs (leaflet 1.9.4).
