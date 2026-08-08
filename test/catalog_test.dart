import 'dart:io';

import 'package:baby_dino_coloring/catalog.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('catalog has 500+ pages, 100+ free, unique ids, valid regions', () {
    final raw = File('assets/pages/pages.json').readAsStringSync();
    final catalog = Catalog.fromJsonString(raw);

    expect(catalog.pages.length, greaterThanOrEqualTo(500));
    expect(catalog.freeCount, greaterThanOrEqualTo(100));
    expect(catalog.categories.length, 10);

    final ids = catalog.pages.map((p) => p.id).toSet();
    expect(ids.length, catalog.pages.length,
        reason: 'page ids must be unique');

    for (final page in catalog.pages) {
      expect(page.title.isNotEmpty, isTrue);
      expect(page.regions.isNotEmpty, isTrue);
      expect(page.regions.where((r) => r.isFillable).length,
          greaterThanOrEqualTo(3),
          reason: '${page.id} should have colorable regions');
    }

    for (final cat in catalog.categories) {
      final pages = catalog.pagesFor(cat.id);
      expect(pages.length, greaterThanOrEqualTo(50));
      expect(pages.where((p) => p.free).length, greaterThanOrEqualTo(10),
          reason: 'every category needs generous free samples');
    }
  });
}
