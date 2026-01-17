
[app]
title = TOP UP GAME MALEO
package.name = topup.games.maleo
package.domain = com.rosyad
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,android,jnius,requests
icon.filename = icon.png
presplash.filename = icon.png
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,on,POST_NOTIFICATIONS,ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
[buildozer]
log_level = 2
warn_on_root = 0
