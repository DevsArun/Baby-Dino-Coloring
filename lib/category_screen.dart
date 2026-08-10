import 'package:flutter/material.dart';

import 'catalog.dart';
import 'coloring_screen.dart';
import 'iap_store.dart';
import 'painter.dart';
import 'parental_gate.dart';
import 'paywall_screen.dart';
import 'progress_store.dart';
import 'routes.dart';

class CategoryScreen extends StatefulWidget {
  const CategoryScreen({super.key, required this.categoryId});

  final String categoryId;

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  Catalog? _catalog;
  final Map<String, PagePaths> _pathCache = {};

  @override
  void initState() {
    super.initState();
    Catalog.load().then((c) {
      if (mounted) {
        setState(() => _catalog = c);
      }
    });
  }

  PagePaths _pathsFor(DinoPage page) {
    return _pathCache.putIfAbsent(page.id, () => PagePaths(page));
  }

  Future<void> _openPage(DinoPage page, bool locked) async {
    if (locked) {
      final ok = await showParentalGate(context);
      if (ok && mounted) {
        await Navigator.of(context).push(smoothRoute(const PaywallScreen()));
      }
      if (mounted) {
        setState(() {});
      }
      return;
    }
    await Navigator.of(context).push(
      smoothRoute(ColoringScreen(page: page)),
    );
    if (mounted) {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final catalog = _catalog;
    final title = catalog?.categories
            .where((c) => c.id == widget.categoryId)
            .map((c) => c.title)
            .join() ??
        '';
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      appBar: AppBar(
        title:
            Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: catalog == null
          ? const Center(child: CircularProgressIndicator())
          : ListenableBuilder(
              listenable: IapStore.instance,
              builder: (context, _) {
                final owned = IapStore.instance.owned;
                final pages = catalog.pagesFor(widget.categoryId);
                return GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate:
                      const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 220,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 0.82,
                  ),
                  itemCount: pages.length,
                  itemBuilder: (context, i) {
                    final page = pages[i];
                    final locked = !page.free && !owned;
                    final fills = ProgressStore.instance.fillsFor(page.id);
                    return _PageCard(
                      page: page,
                      paths: _pathsFor(page),
                      fills: fills,
                      locked: locked,
                      started: fills.isNotEmpty,
                      onTap: () => _openPage(page, locked),
                    );
                  },
                );
              },
            ),
    );
  }
}

class _PageCard extends StatelessWidget {
  const _PageCard({
    required this.page,
    required this.paths,
    required this.fills,
    required this.locked,
    required this.started,
    required this.onTap,
  });

  final DinoPage page;
  final PagePaths paths;
  final Map<String, int> fills;
  final bool locked;
  final bool started;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(22),
      clipBehavior: Clip.antiAlias,
      elevation: 1.5,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Opacity(
                    opacity: locked ? 0.45 : 1,
                    child: PageThumbnail(pagePaths: paths, fills: fills),
                  ),
                  if (locked)
                    const Center(
                      child: CircleAvatar(
                        radius: 26,
                        backgroundColor: Colors.black54,
                        child: Icon(Icons.lock_rounded,
                            color: Colors.white, size: 30),
                      ),
                    ),
                  if (!locked && started)
                    const Positioned(
                      top: 8,
                      right: 8,
                      child: CircleAvatar(
                        radius: 15,
                        backgroundColor: Colors.green,
                        child: Icon(Icons.brush_rounded,
                            color: Colors.white, size: 17),
                      ),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
              child: Text(
                page.title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: Theme.of(context)
                    .textTheme
                    .titleSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
