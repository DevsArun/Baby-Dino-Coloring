import 'dart:math';

import 'package:flutter/material.dart';

import 'strings.dart';

/// Simple math question gate so only a grown-up can continue.
/// Returns true when the gate is passed.
Future<bool> showParentalGate(BuildContext context) async {
  final result = await showDialog<bool>(
    context: context,
    barrierDismissible: true,
    builder: (context) => const _ParentalGateDialog(),
  );
  return result == true;
}

class _ParentalGateDialog extends StatefulWidget {
  const _ParentalGateDialog();

  @override
  State<_ParentalGateDialog> createState() => _ParentalGateDialogState();
}

class _ParentalGateDialogState extends State<_ParentalGateDialog> {
  late int _a;
  late int _b;
  String _entry = '';
  bool _wrong = false;

  @override
  void initState() {
    super.initState();
    _newQuestion();
  }

  void _newQuestion() {
    final rng = Random();
    _a = 3 + rng.nextInt(6); // 3..8
    _b = 4 + rng.nextInt(6); // 4..9
    _entry = '';
    _wrong = false;
  }

  void _tapDigit(int d) {
    if (_entry.length >= 2) {
      return;
    }
    setState(() {
      _entry = '$_entry$d';
      _wrong = false;
    });
    if (_entry.length == 2 || int.parse(_entry) > 9) {
      _check();
    }
  }

  void _check() {
    if (int.tryParse(_entry) == _a * _b) {
      Navigator.of(context).pop(true);
    } else {
      setState(() {
        _newQuestion();
        _wrong = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      title: Text(S.t('gateTitle')),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            S.whatIs(_a, _b),
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            _entry.isEmpty ? '_' : _entry,
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          if (_wrong)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(S.t('tryAgain'),
                  style: const TextStyle(color: Colors.red)),
            ),
          const SizedBox(height: 12),
          for (final row in const [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
          ])
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                for (final d in row)
                  Padding(
                    padding: const EdgeInsets.all(4),
                    child: SizedBox(
                      width: 56,
                      height: 56,
                      child: FilledButton.tonal(
                        onPressed: () => _tapDigit(d),
                        child: Text('$d',
                            style: const TextStyle(fontSize: 22)),
                      ),
                    ),
                  ),
              ],
            ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Padding(
                padding: const EdgeInsets.all(4),
                child: SizedBox(
                  width: 56,
                  height: 56,
                  child: FilledButton.tonal(
                    onPressed: () => _tapDigit(0),
                    child: const Text('0', style: TextStyle(fontSize: 22)),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(4),
                child: SizedBox(
                  width: 120,
                  height: 56,
                  child: OutlinedButton(
                    onPressed: () => setState(() => _entry = ''),
                    child: Text(S.t('clear')),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: Text(S.t('cancel')),
        ),
      ],
    );
  }
}
