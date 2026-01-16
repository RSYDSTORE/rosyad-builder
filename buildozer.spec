
[app]
title = TOP UP GAME MALEO
package.name = com.top.up.games.maleo
package.domain = com
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,android,jnius,requests
icon.filename = icon.png
presplash.filename = icon.png
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,ACCESS_NETWORK_STATE,POST_NOTIFICATIONS,READ_MEDIA_IMAGES,CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,VIBRATE
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = False
android.gradle_dependencies = androidx.core:core:1.6.0
[buildozer]
log_level = 2
warn_on_root = 0
