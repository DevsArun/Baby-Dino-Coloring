import 'package:flutter/material.dart';

import 'catalog.dart';
import 'painter.dart';
import 'progress_store.dart';

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
  int _selected = kPalette[10]; // friendly blue to start
  bool _showGuide = true;
  final List<_FillAction> _undo = [];
  final List<_FillAction> _redo = [];

  /// The colored sample (top) that kids copy onto the blank page (bottom).
  late final Map<String, int> _guide = {
    for (final r in widget.page.regions)
      if (r.isFillable && r.gc != null) r.id: colorFromHex(r.gc!).value,
  };

  @override
  void initState() {
    super.initState();
    _paths = PagePaths(widget.page);
    _fills = ProgressStore.instance.fillsFor(widget.page.id);
  }

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
    });
    ProgressStore.instance.save(widget.page.id, _fills);
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
            tooltip: 'Undo',
            iconSize: 32,
            onPressed: _undo.isEmpty ? null : _undoTap,
            icon: const Icon(Icons.undo_rounded),
          ),
          IconButton(
            tooltip: 'Redo',
            iconSize: 32,
            onPressed: _redo.isEmpty ? null : _redoTap,
            icon: const Icon(Icons.redo_rounded),
          ),
          IconButton(
            tooltip: 'Start over',
            iconSize: 32,
            onPressed: _fills.isEmpty ? null : _clearAll,
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
            child: Row(
              children: [
                if (_showGuide) ...[
                  Container(
                    width: 84,
                    height: 84,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(
                          color: theme.colorScheme.primary, width: 3),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.08),
                          blurRadius: 10,
                        ),
                      ],
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: CustomPaint(
                      painter: ColoringPainter(
                          pagePaths: _paths, fills: _guide),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Copy the colors! \u{1F3A8}',
                      style: theme.textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.w800),
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
                      return GestureDetector(
                        onTapUp: (d) => _tapCanvas(d, constraints),
                        child: Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(24),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.08),
                                blurRadius: 16,
                                offset: const Offset(0, 6),
                              ),
                            ],
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: CustomPaint(
                            painter: ColoringPainter(
                              pagePaths: _paths,
                              fills: Map<String, int>.from(_fills),
                            ),
                            size: Size.infinite,
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
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(28)),
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
                      onTap: () => setState(() => _selected = c),
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
                                color: c == 0xFFFFFFFF || c == 0xFFFDD835
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
    );
  }
}
