import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';

/// Stores coloring progress on device only (no network, no accounts).
class ProgressStore extends ChangeNotifier {
  ProgressStore._();

  static final ProgressStore instance = ProgressStore._();

  final Map<String, Map<String, int>> _fills = {};
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
        data.forEach((pageId, value) {
          final map = <String, int>{};
          (value as Map<String, dynamic>).forEach((rid, c) {
            map[rid] = (c as num).toInt();
          });
          _fills[pageId] = map;
        });
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

  int get startedCount => _fills.values.where((m) => m.isNotEmpty).length;

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
      await file.writeAsString(jsonEncode(_fills));
    } catch (_) {
      // Best effort: losing progress persistence must never crash the app.
    }
  }
}
