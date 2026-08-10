import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Offline background music + sound effects. All audio is generated in-repo
/// (tools/make_audio.py) — 100% royalty-free, no network, no copyright risk.
class SoundStore extends ChangeNotifier {
  SoundStore._();

  static final SoundStore instance = SoundStore._();

  final AudioPlayer _bg = AudioPlayer();
  bool _musicOn = true;
  bool _ready = false;

  bool get musicOn => _musicOn;

  Future<void> init() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _musicOn = prefs.getBool('musicOn') ?? true;
      await _bg.setReleaseMode(ReleaseMode.loop);
      await _bg.setVolume(0.32);
      _ready = true;
      if (_musicOn) {
        await _bg.play(AssetSource('audio/bg_loop.ogg'));
      }
    } catch (_) {
      // Audio must never crash the app; on exotic devices just stay silent.
    }
    notifyListeners();
  }

  Future<void> setMusic(bool on) async {
    _musicOn = on;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('musicOn', on);
    if (!_ready) {
      return;
    }
    try {
      if (on) {
        await _bg.resume();
      } else {
        await _bg.pause();
      }
    } catch (_) {}
  }

  Future<void> _sfx(String asset, {double volume = 0.9}) async {
    try {
      final p = AudioPlayer();
      await p.setVolume(volume);
      await p.play(AssetSource(asset));
      p.onPlayerComplete.first.then((_) => p.dispose());
    } catch (_) {}
  }

  Future<void> pop() => _sfx('audio/pop.ogg', volume: 0.5);

  Future<void> fill() => _sfx('audio/fill.ogg', volume: 0.55);

  Future<void> tada() => _sfx('audio/tada.ogg');
}
