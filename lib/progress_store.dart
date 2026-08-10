import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';

/// Stores coloring progress + earned stars on device only (no network).
/// File format v2: {"fills": {pageId: {regionId: color}}, "stars": [pageId]}
/// (loads the old flat v1 format transparently).
class ProgressStore extends ChangeNotifier {
  ProgressStore._();

  static final ProgressStore instance = ProgressStore._();

  final Map<String, Map<String, int>> _fills = {};
  final Set<String> _starred = {};
  bool _loaded = false;
  File? _file;

  Future<void> ensureLoaded() async {
    if (_loaded) {
      return;
    }
    try {
      final dir = await getApplicationDocumentsDirectory();
      _file = File('${dir.path}/coloring_progress.json');
      final file = _file;
      if (file != null && await file.exists()) {
        final raw = await file.readAsString();
        final data = jsonDecode(raw) as Map<String, dynamic>;
        final fillsData = data.containsKey('fills')
            ? data['fills'] as Map<String, dynamic>
            : data; // v1 flat format
        fillsData.forEach((pageId, value) {
          final map = <String, int>{};
          (value as Map<String, dynamic>).forEach((rid, c) {
            map[rid] = (c as num).toInt();
          });
          _fills[pageId] = map;
        });
        final stars = data['stars'];
        if (stars is List) {
          _starred.addAll(stars.map((e) => e.toString()));
        }
      }
    } catch (_) {
      // Corrupt or unreadable progress file: start fresh.
    }
    _loaded = true;
    notifyListeners();
  }

  Map<String, int> fillsFor(String pageId) {
    return Map<String, int>.from(_fills[pageId] ?? const {});
  }

  bool hasProgress(String pageId) {
    final f = _fills[pageId];
    return f != null && f.isNotEmpty;
  }

  bool isStarred(String pageId) => _starred.contains(pageId);

  int get starCount => _starred.length;

  int get startedCount => _fills.values.where((m) => m.isNotEmpty).length;

  /// Awards a star when a page is completed (idempotent).
  Future<void> awardStar(String pageId) async {
    if (_starred.add(pageId)) {
      notifyListeners();
      await _persist();
    }
  }

  Future<void> save(String pageId, Map<String, int> fills) async {
    if (fills.isEmpty) {
      _fills.remove(pageId);
    } else {
      _fills[pageId] = Map<String, int>.from(fills);
    }
    notifyListeners();
    await _persist();
  }

  Future<void> clear(String pageId) async {
    _fills.remove(pageId);
    notifyListeners();
    await _persist();
  }

  Future<void> _persist() async {
    final file = _file;
    if (file == null) {
      return;
    }
    try {
      await file.writeAsString(
          jsonEncode({'fills': _fills, 'stars': _starred.toList()}));
    } catch (_) {
      // Best effort: losing progress persistence must never crash the app.
    }
  }
}
