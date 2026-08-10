import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

import 'parental_gate.dart';
import 'share_art.dart';

/// In-app "My Gallery": artwork saved on-device only (zero permissions,
/// COPPA-safe). Sharing is gated for grown-ups.
class GalleryScreen extends StatefulWidget {
  const GalleryScreen({super.key});

  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

Future<Directory> galleryDir() async {
  final dir = await getApplicationDocumentsDirectory();
  final gal = Directory('${dir.path}/gallery');
  if (!await gal.exists()) {
    await gal.create(recursive: true);
  }
  return gal;
}

class _GalleryScreenState extends State<GalleryScreen> {
  List<File> _files = [];
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final gal = await galleryDir();
      final files = await gal
          .list()
          .where((e) => e is File && e.path.endsWith('.png'))
          .cast<File>()
          .toList();
      files.sort(
          (a, b) => b.lastModifiedSync().compareTo(a.lastModifiedSync()));
      if (mounted) {
        setState(() {
          _files = files;
          _loaded = true;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _loaded = true);
      }
    }
  }

  Future<void> _share(File file) async {
    final ok = await showParentalGate(context);
    if (ok) {
      await shareArtwork(file);
    }
  }

  Future<void> _view(File file) async {
    await showDialog<void>(
      context: context,
      builder: (context) => Dialog(
        insetPadding: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(24)),
              child: AspectRatio(
                aspectRatio: 1,
                child: Image.file(file, fit: BoxFit.contain),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  FilledButton.icon(
                    onPressed: () => _share(file),
                    icon: const Icon(Icons.share_rounded),
                    label: const Text('Share'),
                  ),
                  OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Close'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
    if (mounted) {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      appBar: AppBar(
        title: const Text('My Gallery \u{1F5BC}\u{FE0F}',
            style: TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: !_loaded
          ? const Center(child: CircularProgressIndicator())
          : _files.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Text(
                      'No artwork yet!\nFinish a dino page and it will '
                      'appear here. \u{1F996}',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                  ),
                )
              : GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate:
                      const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 240,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                  ),
                  itemCount: _files.length,
                  itemBuilder: (context, i) {
                    final file = _files[i];
                    return Material(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(22),
                      clipBehavior: Clip.antiAlias,
                      elevation: 1.5,
                      child: InkWell(
                        onTap: () => _view(file),
                        child: Image.file(file, fit: BoxFit.cover),
                      ),
                    );
                  },
                ),
    );
  }
}
