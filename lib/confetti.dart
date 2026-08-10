import 'dart:math';

import 'package:flutter/material.dart';

/// Lightweight confetti overlay — no packages, pure CustomPainter.
class ConfettiOverlay extends StatefulWidget {
  const ConfettiOverlay({super.key, required this.onDone});

  final VoidCallback onDone;

  @override
  State<ConfettiOverlay> createState() => _ConfettiOverlayState();
}

class _ConfettiOverlayState extends State<ConfettiOverlay>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final List<_Particle> _particles;

  @override
  void initState() {
    super.initState();
    final rng = Random();
    const colors = [
      0xFFE53935, 0xFFFB8C00, 0xFFFDD835, 0xFF43A047, 0xFF039BE5,
      0xFF5E35B1, 0xFFD81B60, 0xFF00ACC1,
    ];
    _particles = List.generate(70, (_) {
      return _Particle(
        x: rng.nextDouble(),
        delay: rng.nextDouble() * 0.35,
        speed: 0.55 + rng.nextDouble() * 0.6,
        size: 6 + rng.nextDouble() * 10,
        color: Color(colors[rng.nextInt(colors.length)]),
        wobble: rng.nextDouble() * 2 * pi,
        spin: rng.nextDouble() * 2 * pi,
      );
    });
    _c = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2300),
    )..forward().then((_) => widget.onDone());
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: AnimatedBuilder(
        animation: _c,
        builder: (context, _) => CustomPaint(
          painter: _ConfettiPainter(_particles, _c.value),
          size: Size.infinite,
        ),
      ),
    );
  }
}

class _Particle {
  _Particle({
    required this.x,
    required this.delay,
    required this.speed,
    required this.size,
    required this.color,
    required this.wobble,
    required this.spin,
  });

  final double x;
  final double delay;
  final double speed;
  final double size;
  final Color color;
  final double wobble;
  final double spin;
}

class _ConfettiPainter extends CustomPainter {
  _ConfettiPainter(this.particles, this.t);

  final List<_Particle> particles;
  final double t;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();
    for (final p in particles) {
      final local = (t - p.delay) / (1 - p.delay);
      if (local <= 0) {
        continue;
      }
      final y = local * p.speed * size.height * 1.25 - p.size;
      if (y > size.height + p.size) {
        continue;
      }
      final x = p.x * size.width +
          sin(local * 6 + p.wobble) * 22;
      final fade = local > 0.8 ? (1 - local) / 0.2 : 1.0;
      paint.color = p.color.withValues(alpha: fade);
      canvas.save();
      canvas.translate(x, y);
      canvas.rotate(p.spin + local * 5);
      canvas.drawRect(
        Rect.fromCenter(
            center: Offset.zero, width: p.size, height: p.size * 0.6),
        paint,
      );
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_ConfettiPainter oldDelegate) => true;
}
