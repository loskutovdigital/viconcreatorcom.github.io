# Как обновить сайт и включить измерение

1. Распакуйте архив. В локальном репозитории замените папки src, dist, seo и файл .github/workflows/pages.yml файлами из обновления. Не удаляйте свою CNAME, если она существует, и не копируйте папку-обёртку внутрь репозитория. Новый код требует src/seo_content.py и src/audit.py: замены только двух старых файлов теперь недостаточно.
2. Замените dist/assets/booking-config.mjs файлом из этого архива: в нём уже новый отдельный Apps Script для Vicon Creator. Старый endpoint Loskutov / Smartlinkella переносить не нужно. Токены остаются в Apps Script.
3. Commit → Push origin. В Settings → Pages Source должен быть GitHub Actions. Дождитесь зелёного deploy. Workflow собирает реальные canonical/hreflang/sitemap и запускает аудит до публикации.
4. После подключения домена в Settings → Pages повторно выполните Run workflow. Не публикуйте одну и ту же версию под несколькими независимыми доменами без выбранного основного адреса и перенаправления.
5. В Search Console добавьте ресурс сайта. Для собственного домена удобно DNS-подтверждение. Если используете URL-prefix и HTML meta tag, скопируйте только значение content из предложенного тега. В GitHub Settings → Secrets and variables → Actions → Variables добавьте GOOGLE_SITE_VERIFICATION с этим значением. Повторно запустите workflow и нажмите Verify в Search Console. Публичный verification-код не является токеном Telegram.
6. Отправьте sitemap.xml и sitemap-images.xml по полному адресу сайта, включая путь репозитория, если он есть. Проверьте главную, EN/NL услуги и одну новую памятку через URL Inspection.
7. Google Analytics G-89KY41JK4Y уже включён в шаблон каждой страницы. Он запускается автоматически; окно согласия и ссылка на настройки cookies удалены по указанию владельца. Убедитесь, что адрес веб-потока в GA4 соответствует вашему опубликованному домену. В настройках потока выключите автоматическое отслеживание взаимодействий с формами, если не хотите считать клики и попытки заполнения событиями. Подтверждённая отправка заявки в этом сайте не объявляется GA-конверсией. Пользователь уже подтвердил записи в Website leads; повторные серверные тесты при выпуске не выполнялись.
8. Для количественного этапа подключите Semrush или выгрузите частотность по файлу seo/keyword-planner-import.txt. Передайте публичный URL, адрес репозитория и экспорт Search Console. Эти сведения позволят проверить опубликованный результат.

Сборка для собственного другого хостинга:
python3 src/generate.py --origin https://YOUR-REAL-DOMAIN --index --portable
python3 src/audit.py --public

Публикуется содержимое dist. Каталог seo — внутренние материалы владельца, в сборку публичных страниц не включён.

Источники: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site ; https://support.google.com/webmasters/answer/9008080 ; https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
