import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

const String kUnlockSku = 'full_library_unlock';

/// Bridge to the Amazon Appstore IAP SDK (native side in MainActivity.kt).
///
/// Rules baked in:
/// - Never short-circuit a purchase with a cached flag: purchase() always
///   sends the real PurchasingService.purchase() call.
/// - Listener is re-registered on every onStart (native side) and
///   getProductData runs on every resume to warm up and verify the SKU.
/// - Watchdog timeouts so buttons never hang.
class IapStore extends ChangeNotifier {
  IapStore._();

  static final IapStore instance = IapStore._();

  static const MethodChannel _channel =
      MethodChannel('com.itschool.babydinocoloring/iap');

  bool _owned = false;
  bool _busy = false;
  String _price = '';
  String _listenerStatus = 'not started';
  String _productStatus = 'not checked';
  String _ownedStatus = 'not checked';
  String _lastMessage = '';
  Timer? _watchdog;

  bool get owned => _owned;
  bool get busy => _busy;
  String get price => _price;
  String get listenerStatus => _listenerStatus;
  String get productStatus => _productStatus;
  String get ownedStatus => _ownedStatus;
  String get lastMessage => _lastMessage;

  Future<void> init() async {
    _channel.setMethodCallHandler(_onNativeCall);
    final prefs = await SharedPreferences.getInstance();
    _owned = prefs.getBool('owned') ?? false;
    if (_owned) {
      _ownedStatus = 'owned (saved on device)';
    }
    notifyListeners();
    try {
      await _channel.invokeMethod<void>('init');
      _listenerStatus = 'registered';
    } on PlatformException catch (e) {
      _listenerStatus = 'error: ${e.code}';
    } on MissingPluginException {
      _listenerStatus = 'unavailable (not on device build)';
    }
    notifyListeners();
    await refresh();
  }

  /// Warm up: verify SKU + query receipts. Safe to call on every resume.
  Future<void> refresh() async {
    try {
      await _channel.invokeMethod<void>('getProductData', {'sku': kUnlockSku});
      await _channel.invokeMethod<void>('getPurchaseUpdates');
    } on PlatformException catch (e) {
      _productStatus = 'error: ${e.code}';
      notifyListeners();
    } on MissingPluginException {
      // Running in a context without the native bridge (tests, etc).
    }
  }

  /// Always sends the REAL purchase call and reports only Amazon's response.
  Future<void> purchase() async {
    if (_busy) {
      return;
    }
    _busy = true;
    _lastMessage = '';
    notifyListeners();
    _startWatchdog();
    try {
      await _channel.invokeMethod<void>('purchase', {'sku': kUnlockSku});
    } on PlatformException catch (e) {
      _finishBusy('Store did not respond (${e.code}). Please try again.');
    } on MissingPluginException {
      _finishBusy(
          'The Amazon Appstore is not available on this device build.');
    }
  }

  Future<void> restore() async {
    if (_busy) {
      return;
    }
    _busy = true;
    _lastMessage = '';
    notifyListeners();
    _startWatchdog();
    try {
      await _channel.invokeMethod<void>('getPurchaseUpdates');
    } on PlatformException catch (e) {
      _finishBusy('Could not check purchases (${e.code}). Please try again.');
    } on MissingPluginException {
      _finishBusy(
          'The Amazon Appstore is not available on this device build.');
    }
  }

  void _startWatchdog() {
    _watchdog?.cancel();
    _watchdog = Timer(const Duration(seconds: 30), () {
      if (_busy) {
        _finishBusy(
            'The store is taking too long. Please check your connection '
            'and try again in a moment.');
      }
    });
  }

  void _finishBusy(String message) {
    _busy = false;
    _lastMessage = message;
    _watchdog?.cancel();
    notifyListeners();
  }

  Future<void> _grant() async {
    _owned = true;
    _ownedStatus = 'owned (receipt verified)';
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('owned', true);
    notifyListeners();
  }

  Future<dynamic> _onNativeCall(MethodCall call) async {
    switch (call.method) {
      case 'onProductData':
        final args = Map<String, dynamic>.from(call.arguments as Map);
        final status = args['status'] as String? ?? 'UNKNOWN';
        if (status == 'SUCCESSFUL') {
          _price = args['price'] as String? ?? '';
          final found = args['found'] == true;
          _productStatus = found ? 'SKU ok ($kUnlockSku)' : 'SKU missing!';
        } else {
          _productStatus = 'product check: $status';
        }
        notifyListeners();
        break;
      case 'onPurchase':
        final args = Map<String, dynamic>.from(call.arguments as Map);
        final status = args['status'] as String? ?? 'UNKNOWN';
        switch (status) {
          case 'SUCCESSFUL':
            await _grant();
            _finishBusy('All dinos unlocked. Happy coloring!');
            break;
          case 'ALREADY_PURCHASED':
            await _grant();
            _finishBusy('Good news - you already own this! Everything is '
                'unlocked.');
            break;
          case 'INVALID_SKU':
            _finishBusy('This item is not available right now. Please try '
                'again later.');
            break;
          case 'NOT_SUPPORTED':
            _finishBusy('Purchases are not supported on this device right '
                'now. Please make sure the Amazon Appstore is set up.');
            break;
          case 'FAILED':
          default:
            _finishBusy('The purchase was not completed. No worries - '
                'nothing was charged.');
            break;
        }
        break;
      case 'onPurchaseUpdates':
        final args = Map<String, dynamic>.from(call.arguments as Map);
        final status = args['status'] as String? ?? 'UNKNOWN';
        final ownedNow = args['owned'] == true;
        if (status == 'SUCCESSFUL') {
          if (ownedNow) {
            await _grant();
            if (_busy) {
              _finishBusy('Your purchase is restored. Everything is '
                  'unlocked!');
            }
          } else {
            _ownedStatus = 'no purchase found';
            if (_busy) {
              _finishBusy('No previous purchase was found on this Amazon '
                  'account.');
            }
          }
        } else {
          if (_busy) {
            _finishBusy('Could not check purchases right now. Please try '
                'again in a moment.');
          }
        }
        notifyListeners();
        break;
      case 'onListenerStatus':
        final args = Map<String, dynamic>.from(call.arguments as Map);
        _listenerStatus = args['status'] as String? ?? 'unknown';
        notifyListeners();
        break;
      default:
        break;
    }
    return null;
  }
}
