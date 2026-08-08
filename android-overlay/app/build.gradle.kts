// Imports MUST stay above the plugins block (Kotlin DSL rule).
import java.io.FileInputStream
import java.util.Properties

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin
    // Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.itschool.babydinocoloring"
    compileSdk = 36
    ndkVersion = "28.2.13676358"

    // All vals INSIDE the android {} block (learned the hard way).
    val keystorePropertiesFile = rootProject.file("key.properties")
    val keystoreProperties = Properties()
    val hasKeystore = keystorePropertiesFile.exists()
    if (hasKeystore) {
        keystoreProperties.load(FileInputStream(keystorePropertiesFile))
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        applicationId = "com.itschool.babydinocoloring"
        minSdk = 22
        targetSdk = 34
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            if (hasKeystore) {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        release {
            if (!hasKeystore) {
                throw GradleException(
                    "key.properties missing! Release builds MUST be signed " +
                        "with the private release keystore (Amazon does not " +
                        "re-sign apps). CI writes this file from secrets."
                )
            }
            signingConfig = signingConfigs.getByName("release")
            // Amazon IAP SDK uses reflection: keep R8 OFF.
            isMinifyEnabled = false
            isShrinkResources = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

repositories {
    google()
    mavenCentral()
}

dependencies {
    // Amazon Appstore SDK from Maven Central (never a local jar).
    implementation("com.amazon.device:amazon-appstore-sdk:3.0.9")
}

flutter {
    source = "../.."
}
