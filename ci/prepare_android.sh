#!/usr/bin/env bash
# Generates the android/ shell with `flutter create` in a THROWAWAY directory
# and copies only android/ back, then applies our overlay (IAP, signing,
# manifest, icons). NEVER run `flutter create --overwrite` on the repo root.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> [1/5] Checking Amazon IAP public key (AppstoreAuthenticationKey.pem)"
if [[ ! -f "AppstoreAuthenticationKey.pem" ]]; then
  echo '::error::AppstoreAuthenticationKey.pem is MISSING from the repo root!'
  echo ''
  echo 'Without this file EVERY purchase returns NOT_SUPPORTED and Amazon'
  echo 'rejects the app ("IAP displays error").'
  echo ''
  echo 'How to get it:'
  echo '  1. Amazon Developer Console -> your app -> Upcoming Version'
  echo '  2. Upload Your App File -> Additional information -> View public key'
  echo '  3. Download AppstoreAuthenticationKey.pem'
  echo '  4. Drag-and-drop it into the ROOT of this GitHub repo'
  exit 1
fi
grep -q 'BEGIN PUBLIC KEY' AppstoreAuthenticationKey.pem || {
  echo '::error::AppstoreAuthenticationKey.pem does not look like a public key file!'
  exit 1
}
echo 'pem OK'

echo "==> [2/5] Generating fresh android/ shell in a throwaway directory"
THROWAWAY="$(mktemp -d)"
pushd "$THROWAWAY" >/dev/null
flutter create --platforms=android -a kotlin \
  --org com.itschool --project-name baby_dino_coloring shell
popd >/dev/null
rm -rf android
cp -R "$THROWAWAY/shell/android" android
rm -rf "$THROWAWAY"

echo "==> [3/5] Applying overlay (IAP bridge, signing config, manifest, icons)"
# Remove the generated MainActivity (wrong package path) before overlaying.
rm -rf android/app/src/main/kotlin
cp -R android-overlay/. android/

echo "==> [4/5] Installing Amazon IAP public key into app assets"
mkdir -p android/app/src/main/assets
cp AppstoreAuthenticationKey.pem android/app/src/main/assets/AppstoreAuthenticationKey.pem

echo "==> [5/5] Sanity checks"
test -f android/app/build.gradle.kts
test -f android/app/src/main/AndroidManifest.xml
test -f android/app/src/main/kotlin/com/itschool/babydinocoloring/MainActivity.kt
test -f android/app/src/main/assets/AppstoreAuthenticationKey.pem
grep -q 'com.amazon.device.iap.ResponseReceiver' android/app/src/main/AndroidManifest.xml
grep -q 'amazon-appstore-sdk:3.0.9' android/app/build.gradle.kts
grep -q 'uses-permission' android/app/src/main/AndroidManifest.xml && {
  echo '::error::Manifest must declare ZERO permissions!'
  exit 1
}
echo 'Android shell ready.'
