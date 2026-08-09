import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

/// One colorable (or fixed decoration) region of a page.
class Region {
  Region({
    required this.id,
    required this.d,
    required this.kind,
    this.color,
    this.gc,
    this.stroke = false,
    this.strokeWidth = 7,
  });

  factory Region.fromJson(Map<String, dynamic> json) {
    return Region(
      id: json['id'] as String,
      d: json['d'] as String,
      kind: json['kind'] as String,
      color: json['color'] as String?,
      gc: json['gc'] as String?,
      stroke: json['stroke'] == true,
      strokeWidth: (json['sw'] as num?)?.toDouble() ?? 7,
    );
  }

  final String id;
  final String d;
  final String kind; // 'fill' | 'fixed'
  final String? color;
  final String? gc; // guide color for the colored sample kids copy
  final bool stroke;
  final double strokeWidth;

  bool get isFillable => kind == 'fill';
}

class DinoPage {
  DinoPage({
    required this.id,
    required this.title,
    required this.category,
    required this.free,
    required this.regions,
  });

  factory DinoPage.fromJson(Map<String, dynamic> json) {
    return DinoPage(
      id: json['id'] as String,
      title: json['title'] as String,
      category: json['category'] as String,
      free: json['free'] == true,
      regions: (json['regions'] as List<dynamic>)
          .map((r) => Region.fromJson(r as Map<String, dynamic>))
          .toList(),
    );
  }

  final String id;
  final String title;
  final String category;
  final bool free;
  final List<Region> regions;
}

class DinoCategory {
  DinoCategory({required this.id, required this.title});

  factory DinoCategory.fromJson(Map<String, dynamic> json) {
    return DinoCategory(
      id: json['id'] as String,
      title: json['title'] as String,
    );
  }

  final String id;
  final String title;
}

class Catalog {
  Catalog({required this.categories, required this.pages});

  factory Catalog.fromJsonString(String raw) {
    final data = jsonDecode(raw) as Map<String, dynamic>;
    return Catalog(
      categories: (data['categories'] as List<dynamic>)
          .map((c) => DinoCategory.fromJson(c as Map<String, dynamic>))
          .toList(),
      pages: (data['pages'] as List<dynamic>)
          .map((p) => DinoPage.fromJson(p as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<DinoCategory> categories;
  final List<DinoPage> pages;

  static Catalog? _cached;

  static Future<Catalog> load() async {
    final cached = _cached;
    if (cached != null) {
      return cached;
    }
    final raw = await rootBundle.loadString('assets/pages/pages.json');
    final catalog = Catalog.fromJsonString(raw);
    _cached = catalog;
    return catalog;
  }

  List<DinoPage> pagesFor(String categoryId) {
    return pages.where((p) => p.category == categoryId).toList();
  }

  int get freeCount => pages.where((p) => p.free).length;
}
