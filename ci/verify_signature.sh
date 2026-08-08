#!/usr/bin/env bash
# Verifies the release APK is signed with OUR private release keystore.
# Fails loudly on debug signatures or certificate mismatch.
set -euo pipefail

APK="build/app/outputs/flutter-apk/app-release.apk"
KEYSTORE="android/release.jks"

test -f "$APK" || { echo "::error::$APK not found"; exit 1; }
test -f "$KEYSTORE" || { echo "::error::$KEYSTORE not found"; exit 1; }

# Newest apksigner available in the runner's SDK.
APKSIGNER="$(find "${ANDROID_HOME:-$ANDROID_SDK_ROOT}/build-tools" -name apksigner | sort -V | tail -1)"
echo "Using apksigner: $APKSIGNER"

OUT="$("$APKSIGNER" verify --verbose --print-certs "$APK")"
echo "$OUT"

if echo "$OUT" | grep -qi 'Android Debug'; then
  echo '::error::APK is signed with the ANDROID DEBUG key! Amazon will reject it.'
  exit 1
fi

# Parse the V2 signer digest line (note the "V2 Signer" prefix; fall back to
# the plain "Signer #1" form for newer apksigner output).
APK_SHA="$(echo "$OUT" \
  | grep -Ei '(V2 )?Signer( #1)?:? certificate SHA-256 digest' \
  | head -1 | grep -Eo '[0-9a-f]{64}')"

if [[ -z "$APK_SHA" ]]; then
  echo '::error::Could not parse the signer SHA-256 digest from apksigner output.'
  exit 1
fi

# The keystore certificate's own SHA-256.
KS_SHA="$(keytool -exportcert -alias "$SIGNING_KEY_ALIAS" \
  -keystore "$KEYSTORE" -storepass "$SIGNING_STORE_PASSWORD" 2>/dev/null \
  | sha256sum | cut -d' ' -f1)"

echo "APK  signer SHA-256: $APK_SHA"
echo "Keystore   SHA-256: $KS_SHA"

if [[ "$APK_SHA" != "$KS_SHA" ]]; then
  echo '::error::Signature mismatch! APK is NOT signed with our release keystore.'
  exit 1
fi

echo 'Signature verified: release APK is signed with our private keystore.'
