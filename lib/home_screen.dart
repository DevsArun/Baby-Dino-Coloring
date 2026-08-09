import 'package:flutter/material.dart';

import 'catalog.dart';
import 'category_screen.dart';
import 'iap_store.dart';
import 'painter.dart';
import 'parental_gate.dart';
import 'paywall_screen.dart';
import 'progress_store.dart';
import 'strings.dart';

const List<int> kCategoryColors = [
  0xFFFFE0B2, 0xFFC8E6C9, 0xFFB3E5FC, 0xFFD1C4E9,
  0xFFF8BBD0, 0xFFFFF9C4, 0xFFB2DFDB, 0xFFFFCCBC,
];

const Map<String, String> kCategoryEmoji = {
  'predators': '\u{1F996}',
  'raptors': '\u{1FAB6}',
  'horned': '\u{1F98F}',
  'longnecks': '\u{1F995}',
  'armored': '\u{1F6E1}\u{FE0F}',
  'flyers': '\u{1F985}',
  'sea': '\u{1F30A}',
  'crested': '\u{1F986}',
  'babies': '\u{1F423}',
  'party': '\u{1F389}',
};

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Catalog? _catalog;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    await ProgressStore.instance.ensureLoaded();
    final catalog = await Catalog.load();
    if (mounted) {
      setState(() => _catalog = catalog);
    }
  }

  Future<void> _openParentArea() async {
    final ok = await showParentalGate(context);
    if (ok && mounted) {
      await Navigator.of(context).push(
        MaterialPageRoute<void>(builder: (_) => const PaywallScreen()),
      );
      if (mounted) {
        setState(() {});
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final catalog = _catalog;
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      body: catalog == null
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: ListenableBuilder(
                listenable: IapStore.instance,
                builder: (context, _) {
                  final owned = IapStore.instance.owned;
                  return CustomScrollView(
                    slivers: [
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: const EdgeInsets.fromLTRB(20, 16, 12, 4),
                          child: Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Baby Dino Coloring',
                                      style: Theme.of(context)
                                          .textTheme
                                          .headlineMedium
                                          ?.copyWith(
                                              fontWeight: FontWeight.w900),
                                    ),
                                    Text(
                                      owned
                                          ? S.allUnlocked(
                                              catalog.pages.length)
                                          : S.freeHaveFun(catalog.freeCount),
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium,
                                    ),
                                  ],
                                ),
                              ),
                              IconButton(
                                tooltip: S.t('forGrownUps'),
                                iconSize: 34,
                                onPressed: _openParentArea,
                                icon: const Icon(
                                    Icons.family_restroom_rounded),
                              ),
                            ],
                          ),
                        ),
                      ),
                      if (!owned)
                        SliverToBoxAdapter(
                          child: Padding(
                            padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
                            child: Material(
                              color: const Color(0xFF43A047),
                              borderRadius: BorderRadius.circular(24),
                              clipBehavior: Clip.antiAlias,
                              child: InkWell(
                                onTap: _openParentArea,
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 20, vertical: 16),
                                  child: Row(
                                    children: [
                                      const Text('\u{1F996}',
                                          style: TextStyle(fontSize: 34)),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              S.t('unlockTitle'),
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 17,
                                                fontWeight: FontWeight.w800,
                                              ),
                                            ),
                                            Text(
                                              '${S.t('unlockAll')} - ${IapStore.instance.price.isEmpty ? '\$3.99' : IapStore.instance.price}',
                                              style: const TextStyle(
                                                color: Colors.white70,
                                                fontSize: 14,
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      const Icon(Icons.lock_open_rounded,
                                          color: Colors.white, size: 30),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      SliverPadding(
                        padding: const EdgeInsets.all(16),
                        sliver: SliverGrid(
                          gridDelegate:
                              const SliverGridDelegateWithMaxCrossAxisExtent(
                            maxCrossAxisExtent: 340,
                            mainAxisSpacing: 16,
                            crossAxisSpacing: 16,
                            childAspectRatio: 1.5,
                          ),
                          delegate: SliverChildBuilderDelegate(
                            (context, i) {
                              final cat = catalog.categories[i];
                              final pages = catalog.pagesFor(cat.id);
                              final freeCount =
                                  pages.where((p) => p.free).length;
                              return _CategoryCard(
                                category: cat,
                                color: Color(kCategoryColors[
                                    i % kCategoryColors.length]),
                                emoji: kCategoryEmoji[cat.id] ?? '\u{1F996}',
                                pageCount: pages.length,
                                freeCount: freeCount,
                                owned: owned,
                                samplePage: pages.first,
                              );
                            },
                            childCount: catalog.categories.length,
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
    );
  }
}

class _CategoryCard extends StatelessWidget {
  const _CategoryCard({
    required this.category,
    required this.color,
    required this.emoji,
    required this.pageCount,
    required this.freeCount,
    required this.owned,
    required this.samplePage,
  });

  final DinoCategory category;
  final Color color;
  final String emoji;
  final int pageCount;
  final int freeCount;
  final bool owned;
  final DinoPage samplePage;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color,
      borderRadius: BorderRadius.circular(28),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute<void>(
              builder: (_) => CategoryScreen(categoryId: category.id),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(emoji, style: const TextStyle(fontSize: 40)),
                    const SizedBox(height: 6),
                    Text(
                      category.title,
                      style: Theme.of(context)
                          .textTheme
                          .titleLarge
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      owned
                          ? '$pageCount pages'
                          : S.freeOf(freeCount, pageCount),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(18),
                child: SizedBox(
                  width: 96,
                  height: 96,
                  child: ColoredBox(
                    color: Colors.white,
                    child: PageThumbnail(
                      pagePaths: PagePaths(samplePage),
                      fills: const {},
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
