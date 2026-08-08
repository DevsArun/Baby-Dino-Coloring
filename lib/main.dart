import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'home_screen.dart';
import 'iap_store.dart';
import 'progress_store.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
    DeviceOrientation.portraitUp,
  ]);
  runApp(const BabyDinoApp());
}

class BabyDinoApp extends StatefulWidget {
  const BabyDinoApp({super.key});

  @override
  State<BabyDinoApp> createState() => _BabyDinoAppState();
}

class _BabyDinoAppState extends State<BabyDinoApp>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    ProgressStore.instance.ensureLoaded();
    IapStore.instance.init();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // Warm up IAP and re-verify the SKU every time we come back.
      IapStore.instance.refresh();
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(seedColor: const Color(0xFF43A047));
    return MaterialApp(
      title: 'Baby Dino Coloring',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: scheme,
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFFFF6E9),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFFFF6E9),
          elevation: 0,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
