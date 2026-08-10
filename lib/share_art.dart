import 'dart:io';

import 'package:share_plus/share_plus.dart';

/// Shares the saved artwork image with the app name attached (free
/// promotion). Uses the native Android share sheet — zero permissions,
/// fully offline-capable. Call sites sit behind the parental gate.
Future<void> shareArtwork(File file) async {
  await Share.shareXFiles(
    [XFile(file.path)],
    text: 'Made with Baby Dino Coloring \u{1F996} — get it on the '
        'Amazon Appstore!',
  );
}
