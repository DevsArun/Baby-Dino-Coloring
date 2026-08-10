import 'dart:async';

import 'package:flutter/material.dart';

import 'home_screen.dart';
import 'routes.dart';

/// Animated splash: dino logo bounces in, app name fades, then home.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final Animation<double> _scale;
  late final Animation<double> _fade;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    );
    _scale = CurvedAnimation(parent: _c, curve: Curves.elasticOut);
    _fade = CurvedAnimation(
      parent: _c,
      curve: const Interval(0.45, 1.0, curve: Curves.easeIn),
    );
    _c.forward();
    _timer = Timer(const Duration(milliseconds: 1900), _goHome);
  }

  void _goHome() {
    if (!mounted) {
      return;
    }
    Navigator.of(context).pushReplacement(smoothRoute(const HomeScreen()));
  }

  @override
  void dispose() {
    _timer?.cancel();
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ScaleTransition(
                scale: _scale,
                child: Container(
                  width: 150,
                  height: 150,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(38),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.12),
                        blurRadius: 24,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Image.asset('assets/brand/icon_512.png'),
                ),
              ),
              const SizedBox(height: 26),
              FadeTransition(
                opacity: _fade,
                child: Column(
                  children: [
                    Text(
                      'Baby Dino Coloring',
                      style:
                          Theme.of(context).textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.w900,
                                color: const Color(0xFF2E7D32),
                              ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Tap, color, roar! \u{1F996}',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
