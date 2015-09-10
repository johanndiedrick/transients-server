mongo <mongo_uri> -u <dbuser> -p <dbpassword>
db.geosounds.update({}, {$rename:{"sound_url":"sound_url_mp3"}}, false, true);
