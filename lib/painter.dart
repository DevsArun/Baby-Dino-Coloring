import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import 'catalog.dart';
import 'path_parser.dart';

const double kCanvasSize = 1024;

/// Pre-parsed paths for a page, cached so hit-testing and painting are fast.
class PagePaths {
  PagePaths(DinoPage page)
      : regions = page.regions,
        paths = {
          for (final r in page.regions) r.id: parseSvgPath(r.d),
        };

  final List<Region> regions;
  final Map<String, ui.Path> paths;

  /// Returns the topmost fillable region at [point] (in 1024-space).
  String? hitTest(Offset point) {
    for (var i = regions.length - 1; i >= 0; i--) {
      final r = regions[i];
      if (!r.isFillable) {
        continue;
      }
      final path = paths[r.id];
      if (path != null && path.contains(point)) {
        return r.id;
      }
    }
    return null;
  }
}

Color colorFromHex(String hex) {
  final cleaned = hex.replaceFirst('#', '');
  return Color(int.parse('FF$cleaned', radix: 16));
}

class ColoringPainter extends CustomPainter {
  ColoringPainter({
    required this.pagePaths,
    required this.fills,
    this.outlineColor = const Color(0xFF222222),
  });

  final PagePaths pagePaths;
  final Map<String, int> fills; // regionId -> ARGB color value
  final Color outlineColor;

  @override
  void paint(Canvas canvas, Size size) {
    final scale = size.width / kCanvasSize;
    canvas.save();
    canvas.scale(scale, scale);

    final fillPaint = Paint()..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..color = outlineColor;

    for (final r in pagePaths.regions) {
      final path = pagePaths.paths[r.id];
      if (path == null) {
        continue;
      }
      if (r.isFillable) {
        final value = fills[r.id];
        fillPaint.color = value != null ? Color(value) : Colors.white;
        canvas.drawPath(path, fillPaint);
        strokePaint.strokeWidth = 6;
        canvas.drawPath(path, strokePaint);
      } else if (r.stroke) {
        strokePaint.strokeWidth = r.strokeWidth;
        canvas.drawPath(path, strokePaint);
        strokePaint.strokeWidth = 6;
      } else {
        fillPaint.color =
            r.color != null ? colorFromHex(r.color!) : outlineColor;
        canvas.drawPath(path, fillPaint);
      }
    }
    canvas.restore();
  }

  @override
  bool shouldRepaint(ColoringPainter oldDelegate) {
    return oldDelegate.fills != fills || oldDelegate.pagePaths != pagePaths;
  }
}

/// Small static preview of a page (used in grids / gallery).
class PageThumbnail extends StatelessWidget {
  const PageThumbnail({
    super.key,
    required this.pagePaths,
    required this.fills,
  });

  final PagePaths pagePaths;
  final Map<String, int> fills;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1,
      child: CustomPaint(
        painter: ColoringPainter(pagePaths: pagePaths, fills: fills),
      ),
    );
  }
}
