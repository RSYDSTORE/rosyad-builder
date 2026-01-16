[app]
title = TOP UP GAME MALEO
package.name = maleo
package.domain = com.rosyad.store
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 3.0
requirements = python3,kivy,android,jnius,requests

icon.filename = icon.png
presplash.filename = icon.png
orientation = portrait
fullscreen = 1

# PERMISSIONS (NO BACKGROUND SERVICE - ANTI CRASH)
android.permissions = INTERNET,ACCESS_NETWORK_STATE,POST_NOTIFICATIONS,VIBRATE,WAKE_LOCK

android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.gradle_dependencies = androidx.core:core:1.6.0

[buildozer]
log_level = 2
warn_on_root = 0
