# Amazon Appstore SDK uses reflection. R8/minify is disabled anyway, but keep
# these rules as a safety net in case minification is ever re-enabled.
-dontwarn com.amazon.**
-keep class com.amazon.** { *; }
-keepattributes *Annotation*
