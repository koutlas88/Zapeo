"""Ajusta el proyecto Android generado por Capacitor para que funcione en Android TV / Google TV."""
import os
import pathlib
import re
import shutil

root = pathlib.Path("android")
manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
text = manifest.read_text(encoding="utf-8")

# 1) Banner del lanzador de TV
text = text.replace("<application", '<application android:banner="@drawable/banner"', 1)

# 2) Declarar que sirve para TV y que no necesita pantalla táctil
features = (
    '    <uses-feature android:name="android.software.leanback" android:required="false" />\n'
    '    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />\n'
)
if "android.software.leanback" not in text:
    text = text.replace("<application", features + "    <application", 1)

# 3) Que aparezca en la lista de apps de la tele
launcher = '<category android:name="android.intent.category.LAUNCHER" />'
leanback = '<category android:name="android.intent.category.LEANBACK_LAUNCHER" />'
if leanback not in text:
    assert launcher in text, "No se encontró la categoría LAUNCHER en el manifiesto"
    text = text.replace(launcher, launcher + "\n                " + leanback, 1)

manifest.write_text(text, encoding="utf-8")

# 4) Copiar el banner
drawable = root / "app" / "src" / "main" / "res" / "drawable"
drawable.mkdir(parents=True, exist_ok=True)
shutil.copy("tv/banner.png", drawable / "banner.png")

# 5) Número de versión creciente, para que cada APK nuevo se pueda instalar encima del anterior
build_number = os.environ.get("BUILD_NUMBER", "1")
gradle = root / "app" / "build.gradle"
g = gradle.read_text(encoding="utf-8")
g = re.sub(r"versionCode\s+\d+", "versionCode " + build_number, g, count=1)
g = re.sub(r'versionName\s+"[^"]*"', 'versionName "0.3.' + build_number + '"', g, count=1)
gradle.write_text(g, encoding="utf-8")

print("Proyecto ajustado para Android TV, versión", build_number)
