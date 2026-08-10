import 'dart:async';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import 'catalog.dart';
import 'confetti.dart';
import 'gallery_screen.dart';
import 'painter.dart';
import 'parental_gate.dart';
import 'progress_store.dart';
import 'share_art.dart';
import 'sound_store.dart';

const List<int> kPalette = [
  0xFFE53935, 0xFFF4511E, 0xFFFB8C00, 0xFFFFB300, 0xFFFDD835, 0xFFC0CA33,
  0xFF7CB342, 0xFF43A047, 0xFF00897B, 0xFF00ACC1, 0xFF039BE5, 0xFF1E88E5,
  0xFF3949AB, 0xFF5E35B1, 0xFF8E24AA, 0xFFD81B60, 0xFFF06292, 0xFFFFAB91,
  0xFFA1887F, 0xFF6D4C41, 0xFF90A4AE, 0xFF546E7A, 0xFF222222, 0xFFFFFFFF,
];

class _FillAction {
  _FillAction(this.regionId, this.oldColor, this.newColor);

  final String regionId;
  final int? oldColor;
  final int newColor;
}

class ColoringScreen extends StatefulWidget {
  const ColoringScreen({super.key, required this.page});

  final DinoPage page;

  @override
  State<ColoringScreen> createState() => _ColoringScreenState();
}

class _ColoringScreenState extends State<ColoringScreen> {
  late final PagePaths _paths;
  late Map<String, int> _fills;
  late final int _fillableCount;
  int _selected = kPalette[10]; // friendly blue to start
  bool _showGuide = true;
  bool _celebrating = false;
  bool _celebrated = false;
  double _bounce = 1.0;
  Timer? _bounceTimer;
  Timer? _confettiTimer;
  final List<_FillAction> _undo = [];
  final List<_FillAction> _redo = [];

  /// The colored sample (top) that kids copy onto the blank page (bottom).
  late final Map<String, int> _guide = {
    for (final r in widget.page.regions)
      if (r.isFillable && r.gc != null) r.id: colorFromHex(r.gc!).toARGB32(),
  };

  @override
  void initState() {
    super.initState();
    _paths = PagePaths(widget.page);
    _fills = ProgressStore.instance.fillsFor(widget.page.id);
    _fillableCount =
        widget.page.regions.where((r) => r.isFillable).length;
  }

  @override
  void dispose() {
    _bounceTimer?.cancel();
    _confettiTimer?.cancel();
    super.dispose();
  }

  int get _percent => _fillableCount == 0
      ? 0
      : (100 * _fills.length / _fillableCount).round().clamp(0, 100);

  void _tapCanvas(TapUpDetails details, BoxConstraints constraints) {
    final side = constraints.biggest.shortestSide;
    final scale = kCanvasSize / side;
    final p = Offset(
      details.localPosition.dx * scale,
      details.localPosition.dy * scale,
    );
    final id = _paths.hitTest(p);
    if (id == null) {
      return;
    }
    final old = _fills[id];
    if (old == _selected) {
      return;
    }
    setState(() {
      _undo.add(_FillAction(id, old, _selected));
      _redo.clear();
      _fills[id] = _selected;
      _bounce = 1.02;
    });
    SoundStore.instance.fill();
    _bounceTimer?.cancel();
    _bounceTimer = Timer(const Duration(milliseconds: 140), () {
      if (mounted) {
        setState(() => _bounce = 1.0);
      }
    });
    ProgressStore.instance.save(widget.page.id, _fills);
    _checkComplete();
  }

  void _checkComplete() {
    if (_celebrated ||
        _fillableCount == 0 ||
        _fills.length < _fillableCount) {
      return;
    }
    _celebrated = true;
    _celebrate();
  }

  Future<void> _celebrate() async {
    setState(() => _celebrating = true);
    SoundStore.instance.tada();
    final file = await _saveArtwork();
    await ProgressStore.instance.awardStar(widget.page.id);
    _confettiTimer = Timer(const Duration(milliseconds: 2400), () async {
      if (!mounted) {
        return;
      }
      setState(() => _celebrating = false);
      await _showCompletionDialog(file);
    });
  }

  Future<File?> _saveArtwork() async {
    try {
      const size = Size(512, 512);
      final recorder = ui.PictureRecorder();
      final canvas = Canvas(recorder);
      canvas.drawRect(
          Offset.zero & size, Paint()..color = Colors.white);
      ColoringPainter(
        pagePaths: _paths,
        fills: Map<String, int>.from(_fills),
      ).paint(canvas, size);
      final img = await recorder.endRecording().toImage(512, 512);
      final bytes = await img.toByteData(format: ui.ImageByteFormat.png);
      if (bytes == null) {
        return null;
      }
      final gal = await galleryDir();
      final file = File('${gal.path}/${widget.page.id}.png');
      await file.writeAsBytes(bytes.buffer.asUint8List());
      return file;
    } catch (_) {
      return null;
    }
  }

  Future<void> _showCompletionDialog(File? file) async {
    if (!mounted) {
      return;
    }
    await showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
        title: const Text('Awesome! \u{2B50}\u{1F996}'),
        content: Text(
          'You finished "${widget.page.title}"!\nYou earned a star and '
          'your artwork is saved in My Gallery \u{1F5BC}\u{FE0F}',
          style: const TextStyle(fontSize: 16, height: 1.5),
        ),
        actions: [
          if (file != null)
            TextButton.icon(
              onPressed: () async {
                final ok = await showParentalGate(context);
                if (ok) {
                  await shareArtwork(file);
                }
              },
              icon: const Icon(Icons.share_rounded),
              label: const Text('Share'),
            ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Keep coloring'),
          ),
        ],
      ),
    );
  }

  void _undoTap() {
    if (_undo.isEmpty) {
      return;
    }
    final a = _undo.removeLast();
    setState(() {
      _redo.add(a);
      if (a.oldColor == null) {
        _fills.remove(a.regionId);
      } else {
        _fills[a.regionId] = a.oldColor!;
      }
    });
    ProgressStore.instance.save(widget.page.id, _fills);
  }

  void _redoTap() {
    if (_redo.isEmpty) {
      return;
    }
    final a = _redo.removeLast();
    setState(() {
      _undo.add(a);
      _fills[a.regionId] = a.newColor;
    });
    ProgressStore.instance.save(widget.page.id, _fills);
  }

  Future<void> _clearAll() async {
    if (_fills.isEmpty) {
      return;
    }
    setState(() {
      _undo.clear();
      _redo.clear();
      _fills = {};
    });
    await ProgressStore.instance.clear(widget.page.id);
  }

  Future<void> _saveManual() async {
    final file = await _saveArtwork();
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        behavior: SnackBarBehavior.floating,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        content: Text(file != null
            ? 'Saved to My Gallery! \u{1F5BC}\u{FE0F}'
            : 'Could not save right now'),
      ),
    );
  }

  void _showBigSample() {
    showDialog<void>(
      context: context,
      builder: (context) => Dialog(
        insetPadding: const EdgeInsets.all(14),
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(24)),
              child: AspectRatio(
                aspectRatio: 1,
                child: CustomPaint(
                  painter: ColoringPainter(pagePaths: _paths, fills: _guide),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: FilledButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.brush_rounded),
                label: const Text('Copy these colors!'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      appBar: AppBar(
        title: Text(
          widget.page.title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            tooltip: 'Save to My Gallery',
            iconSize: 30,
            onPressed: _saveManual,
            icon: const Icon(Icons.photo_camera_rounded),
          ),
          IconButton(
            tooltip: 'Undo',
            iconSize: 30,
            onPressed: _undo.isEmpty ? null : _undoTap,
            icon: const Icon(Icons.undo_rounded),
          ),
          IconButton(
            tooltip: 'Redo',
            iconSize: 30,
            onPressed: _redo.isEmpty ? null : _redoTap,
            icon: const Icon(Icons.redo_rounded),
          ),
          IconButton(
            tooltip: 'Start over',
            iconSize: 30,
            onPressed: _fills.isEmpty ? null : _clearAll,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: Stack(
        children: [
          Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
                child: Row(
                  children: [
                    if (_showGuide) ...[
                      GestureDetector(
                        onTap: _showBigSample,
                        child: Container(
                          width: 96,
                          height: 96,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(
                                color: theme.colorScheme.primary, width: 3),
                            boxShadow: [
                              BoxShadow(
                                color:
                                    Colors.black.withValues(alpha: 0.08),
                                blurRadius: 10,
                              ),
                            ],
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Stack(
                            fit: StackFit.expand,
                            children: [
                              CustomPaint(
                                painter: ColoringPainter(
                                    pagePaths: _paths, fills: _guide),
                              ),
                              const Positioned(
                                right: 4,
                                bottom: 4,
                                child: Icon(Icons.zoom_in_rounded,
                                    size: 22, color: Colors.black45),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Copy the colors! \u{1F3A8}',
                              style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w800),
                            ),
                            const SizedBox(height: 4),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: LinearProgressIndicator(
                                value: _percent / 100,
                                minHeight: 10,
                                backgroundColor: Colors.black12,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text('$_percent% colored',
                                style: theme.textTheme.bodySmall),
                          ],
                        ),
                      ),
                    ] else
                      const Spacer(),
                    IconButton(
                      tooltip: _showGuide ? 'Hide sample' : 'Show sample',
                      iconSize: 30,
                      onPressed: () =>
                          setState(() => _showGuide = !_showGuide),
                      icon: Icon(_showGuide
                          ? Icons.visibility_rounded
                          : Icons.visibility_off_rounded),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: AspectRatio(
                      aspectRatio: 1,
                      child: LayoutBuilder(
                        builder: (context, constraints) {
                          return AnimatedScale(
                            scale: _bounce,
                            duration: const Duration(milliseconds: 140),
                            curve: Curves.easeOut,
                            child: Container(
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(24),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black
                                        .withValues(alpha: 0.08),
                                    blurRadius: 16,
                                    offset: const Offset(0, 6),
                                  ),
                                ],
                              ),
                              clipBehavior: Clip.antiAlias,
                              child: InteractiveViewer(
                                minScale: 1,
                                maxScale: 4,
                                panEnabled: true,
                                scaleEnabled: true,
                                child: GestureDetector(
                                  onTapUp: (d) => _tapCanvas(d, constraints),
                                  child: CustomPaint(
                                    painter: ColoringPainter(
                                      pagePaths: _paths,
                                      fills: Map<String, int>.from(_fills),
                                    ),
                                    size: Size.infinite,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                ),
              ),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(28)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 12,
                    ),
                  ],
                ),
                padding: const EdgeInsets.fromLTRB(12, 12, 12, 16),
                child: SafeArea(
                  top: false,
                  child: SizedBox(
                    height: 64,
                    child: ListView.separated(
                      scrollDirection: Axis.horizontal,
                      itemCount: kPalette.length,
                      separatorBuilder: (_, __) => const SizedBox(width: 10),
                      itemBuilder: (context, i) {
                        final c = kPalette[i];
                        final selected = c == _selected;
                        return GestureDetector(
                          onTap: () {
                            setState(() => _selected = c);
                            SoundStore.instance.pop();
                          },
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 150),
                            width: selected ? 64 : 52,
                            height: selected ? 64 : 52,
                            decoration: BoxDecoration(
                              color: Color(c),
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: selected
                                    ? theme.colorScheme.primary
                                    : Colors.black12,
                                width: selected ? 4 : 2,
                              ),
                            ),
                            child: selected
                                ? Icon(
                                    Icons.brush_rounded,
                                    color:
                                        c == 0xFFFFFFFF || c == 0xFFFDD835
                                            ? Colors.black54
                                            : Colors.white,
                                  )
                                : null,
                          ),
                        );
                      },
                    ),
                  ),
                ),
              ),
            ],
          ),
          if (_celebrating)
            Positioned.fill(
              child: ConfettiOverlay(
                onDone: () {},
              ),
            ),
        ],
      ),
    );
  }
}
