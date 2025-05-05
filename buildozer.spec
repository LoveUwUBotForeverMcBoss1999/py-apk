[app]

# Title of your application
title = Place Book

# Package name
package.name = placebook

# Package domain (needed for android/ios packaging)
package.domain = org.test

# Source code where the main.py live
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Application version
version = 0.1

# Application requirements
requirements = python3,kivy

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientation
orientation = portrait

# Android API level
android.api = 31

# Android SDK version
android.sdk = 31

# Android NDK version
android.ndk = 23b

# Android specific settings
android.minapi = 21
android.accept_sdk_license = True
android.arch = arm64-v8a

# Build directory
# If you set this to a non-empty value, the build will be
# performed into this directory rather than in the current directory.
build_dir = ./build

# Android Gradle settings
android.gradle_dependencies =

# Auto-remove SDL2 from backup, unnecessary on Android
p4a.bootstrap = sdl2

# Icon for your application
# icon.filename = %(source.dir)s/data/icon.png

# If True, application will be translated for supported languages:
p4a.hook =

# Android application meta-data
android.meta_data =

# Comma separated list of screens:
# Presplash while application loading
# presplash.filename = %(source.dir)s/data/presplash.png

# Automatic fullscreen mode
fullscreen = 0

# Application android specific intent filters
# android.intent_filters =

# (list) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (string) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a