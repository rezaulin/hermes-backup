---
name: android-apk-builder
description: Build native Android APK/AAB from scratch on a headless Linux VPS without Android Studio.
triggers:
  - "build android app"
  - "create APK"
  - "android development"
  - "build mobile app"
---

# Android APK Builder on Linux VPS

Build native Android (Kotlin) apps on a headless server. No Android Studio needed.

## When to Use
- Building simple native Android apps (XML layouts + Kotlin)
- User wants a Play Store-ready APK/AAB
- No desktop GUI available (VPS/headless)

## Prerequisites Check
```bash
java -version 2>&1    # Need JDK 17+
df -h /               # Need ~5GB free for SDK
free -h               # Need 4GB+ RAM
```

## Step 1: Install JDK 17
```bash
apt update -qq && apt install -y -qq openjdk-17-jdk-headless unzip wget
java -version  # Verify
```

## Step 2: Install Android SDK
```bash
mkdir -p /opt/android-sdk && cd /opt/android-sdk
wget -q "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" -O cmdtools.zip
unzip -q cmdtools.zip
mkdir -p cmdline-tools/latest
mv cmdline-tools/bin cmdline-tools/latest/
mv cmdline-tools/lib cmdline-tools/latest/
mv cmdline-tools/NOTICE.txt cmdline-tools/latest/ 2>/dev/null
mv cmdline-tools/source.properties cmdline-tools/latest/ 2>/dev/null
rm cmdtools.zip

export ANDROID_HOME=/opt/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

## Step 3: Create Project Structure
```
project/
├── settings.gradle
├── build.gradle              # Project-level (plugin versions)
├── gradle.properties
├── local.properties          # sdk.dir=/opt/android-sdk
├── gradlew + gradle/wrapper/
├── app/
│   ├── build.gradle          # App-level (dependencies, signing)
│   ├── proguard-rules.pro
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/package/app/  # Kotlin activities
│       └── res/
│           ├── layout/       # XML layouts
│           ├── values/       # colors.xml, strings.xml, themes.xml
│           ├── drawable/     # Vector/XML drawables
│           └── mipmap-*/     # App icons (PNG)
```

### Key Build Files

**settings.gradle:**
```groovy
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "AppName"
include ':app'
```

**build.gradle (project):**
```groovy
plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.21' apply false
}
```

**app/build.gradle:**
```groovy
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}
android {
    namespace 'com.package.app'
    compileSdk 34
    defaultConfig {
        applicationId "com.package.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    signingConfigs {
        release {
            storeFile file("keystore.jks")
            storePassword "password"
            keyAlias "alias"
            keyPassword "password"
        }
    }
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = '17' }
    buildFeatures { viewBinding true }
}
dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.cardview:cardview:1.0.0'
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
}
```

## Step 4: Gradle Wrapper
```bash
cd project/
wget -q "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradlew" -O gradlew
chmod +x gradlew
mkdir -p gradle/wrapper
wget -q "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradle/wrapper/gradle-wrapper.jar" -O gradle/wrapper/gradle-wrapper.jar
wget -q "https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradle/wrapper/gradle-wrapper.properties" -O gradle/wrapper/gradle-wrapper.properties
```

## Step 5: App Icons (Python-generated PNGs)
```python
import struct, zlib
def create_png(size, filepath):
    r,g,b = 76,175,80
    raw = b''.join(b'\x00' + bytes([r,g,b])*size for _ in range(size))
    compressed = zlib.compress(raw, 9)
    def chunk(t,d): c=t+d; return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
    with open(filepath,'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB',size,size,8,2,0,0,0)))
        f.write(chunk(b'IDAT', compressed))
        f.write(chunk(b'IEND', b''))
```

## Step 6: Generate Keystore
```bash
keytool -genkeypair -v -keystore app/keystore.jks -alias myapp \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass mypassword -keypass mypassword \
  -dname "CN=AppName, OU=Dev, O=Org, L=City, ST=State, C=ID"
```

## Step 7: Build
```bash
export ANDROID_HOME=/opt/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
./gradlew assembleRelease --no-daemon
# Output: app/build/outputs/apk/release/app-release.apk
```

## Pitfalls
- **`--no-daemon`** required on low-memory VPS to prevent OOM.
- **Play Store needs AAB**: use `./gradlew bundleRelease` for `.aab` output.
- **ProGuard/R8** may strip needed classes. Add `-keep` rules if release crashes.
- **Gradle wrapper jar** must exist at `gradle/wrapper/gradle-wrapper.jar`.
- **Material components** need `Theme.Material3.*` parent, NOT `Theme.AppCompat`.
- **Replace self-signed keystore** with production keystore before Play Store upload.
- **XML `&` must be `&amp;`**: Any `&` in layout XML (e.g. `android:text="A & B"`) causes build failure. Always escape as `&amp;` in XML attributes. Common in menu labels, descriptions, and hints.
- **RecyclerView + Adapter**: When creating list screens, keep data classes + adapter in the same Activity file for simplicity. Separate files only when adapter is reused across activities.

## Reusing Files Between Projects
When building multiple apps on the same VPS, copy shared files instead of re-downloading:
```bash
# Copy gradle wrapper (saves re-download)
cp -r existing-project/gradle/wrapper/* new-project/gradle/wrapper/
cp existing-project/gradlew new-project/gradlew
chmod +x new-project/gradlew

# Copy keystore for signing (reuse across dev apps)
cp existing-project/app/keystore.jks new-project/app/
```

## Serving APK for Download
When `MEDIA:/path` delivery fails (e.g. Telegram gateway), serve via HTTP:
```bash
# Kill any existing server on that port
pkill -f "python3 -m http.server 8080" 2>/dev/null
cd /path/to/apk/directory
python3 -m http.server 8080 --bind 0.0.0.0 &
curl -s ifconfig.me  # Get public IP
# Link: http://<PUBLIC_IP>:8080/app-release.apk
```

## Advanced Icon Generation (Python)
For custom icons with shapes (not just solid color), draw pixel-by-pixel:
```python
def draw_icon(size):
    pixels = []
    for y in range(size):
        for x in range(size):
            # Heart equation, circles, rectangles...
            heart_val = (hx**2 + hy**2 - 1)**3 - hx**2 * hy**3
            if heart_val < 0:
                pixels.append((255, 255, 255))  # white
            else:
                pixels.append((0, 121, 107))  # bg
    return pixels
```
Use for adaptive-icon fallback (pre-API 26 devices). Adaptive icons (vector XML) are preferred for API 26+.

## SQLite Data Seeding Strategy
For data-heavy apps (dictionaries, catalogs), seed inline from Kotlin:
```kotlin
// Keep all seed data in a separate object/file
object KamusData {
    fun getAll(): List<KataArab> = listOf(
        KataArab(arabic="كَتَبَ", transliteration="kataba", indonesia="menulis", ...),
        // 500+ entries
    )
}

// In SQLiteOpenHelper.onCreate():
private fun seedData(db: SQLiteDatabase) {
    db.beginTransaction()
    try {
        for (w in KamusData.getAll()) {
            // insert each
        }
        db.setTransactionSuccessful()
    } finally {
        db.endTransaction()
    }
}
```
This is simpler than bundling a pre-built `.db` file and works reliably on all devices.

## Writing Large Kotlin Files (Pitfalls)

### Heredoc Timeout
Bash heredocs with 200+ lines of Kotlin data cause terminal timeouts. Instead, use Python to write the file:
```bash
python3 -c "
code = '''package com.example
// your Kotlin code here
'''
with open('/path/to/File.kt','w') as f:
    f.write(code)
print('done')
"
```
Or break into multiple `cat >> file << 'EOF'` appends (Part 1, Part 2, etc.) with ~70 lines max per heredoc.

### Single Quotes in Kotlin Strings (ّayn transliterations)
Arabic transliterations starting with `'` (ayn sound like `'amalun`, `'ilmun`) break Kotlin:
```kotlin
// BROKEN — Kotlin sees char literal
KataArab(arabic="عَمَلٌ", transliteration='amalun', ...)
// FIXED — use double quotes
KataArab(arabic="عَمَلٌ", transliteration="amalun", ...)
```
After writing data, always scan: `grep -n "'[a-zA-Z].*[a-zA-Z]'" File.kt`
Fix with regex: `sed -i "s/'word'/\"word\"/g" File.kt`

### Regex fix-all (Python):
```python
import re
with open('KamusData.kt','r') as f: content = f.read()
content = re.sub(r",'([^']+)',", r',"\1",', content)
with open('KamusData.kt','w') as f: f.write(content)
```

## Keystore Path for Multi-Project Builds
When reusing a keystore across projects, the `storeFile` path in build.gradle is relative to the project root, NOT `app/`:
```groovy
// If keystore is at /root/project/keystore.jks:
storeFile file("keystore.jks")  // relative to project root
// NOT: storeFile file("../other-project/keystore.jks") — fragile
```
Copy keystore to new project root: `cp old-project/keystore.jks new-project/`

## Large Data Files via Delegate
When generating very large Kotlin data files (500+ entries), use `delegate_task` with terminal+file toolsets. The subagent can write the file in isolation without flooding the parent context. Pass all data as context to the goal.

## Writing Large Kotlin Files (Pitfalls)

### Heredoc Timeout
Bash heredocs with 200+ lines of Kotlin data cause terminal timeouts. Instead, use Python to write the file:
```bash
python3 -c "
code = '''package com.example
// your Kotlin code here
'''
with open('/path/to/File.kt','w') as f:
    f.write(code)
print('done')
"
```
Or break into multiple `cat >> file << 'EOF'` appends (Part 1, Part 2, etc.) with ~70 lines max per heredoc.

### Single Quotes in Kotlin Strings (ّayn transliterations)
Arabic transliterations starting with `'` (ayn sound like `'amalun`, `'ilmun`) break Kotlin:
```kotlin
// BROKEN — Kotlin sees char literal
KataArab(arabic="عَمَلٌ", transliteration='amalun', ...)
// FIXED — use double quotes
KataArab(arabic="عَمَلٌ", transliteration="amalun", ...)
```
After writing data, always scan: `grep -n "'[a-zA-Z].*[a-zA-Z]'" File.kt`
Fix with regex: `sed -i "s/'word'/\"word\"/g" File.kt`

### Regex fix-all (Python):
```python
import re
with open('KamusData.kt','r') as f: content = f.read()
content = re.sub(r",'([^']+)',", r',"\1",', content)
with open('KamusData.kt','w') as f: f.write(content)
```

## Keystore Path for Multi-Project Builds
When reusing a keystore across projects, the `storeFile` path in build.gradle is relative to the project root, NOT `app/`:
```groovy
// If keystore is at /root/project/keystore.jks:
storeFile file("keystore.jks")  // relative to project root
// NOT: storeFile file("../other-project/keystore.jks") — fragile
```
Copy keystore to new project root: `cp old-project/keystore.jks new-project/`

## Verified
- Ubuntu 22.04 VPS (4vCPU, 8GB RAM), Gradle 8.5, AGP 8.2.0, Kotlin 1.9.21, JDK 17
- Build time: ~4min debug, ~3.5min release (cached). APK ~2-6MB.
- Tested: Tips Kesehatan (6 features, 2.1MB), Kamus Arab (500+ words, SQLite)
- Tested: Tips Kesehatan app (6 features, 2.1MB release APK)
- Tested: Kamus Arab-Indonesia app (437 words, SQLite search, verb conjugations, categories)
- HTTP serving for APK download when MEDIA: delivery fails on Telegram
- Tested: Tips Kesehatan app (6 features, 2.1MB release APK)
- Tested: Kamus Arab-Indonesia app (437 words, SQLite search, verb conjugations, categories)
- HTTP serving for APK download when MEDIA: delivery fails on Telegram
