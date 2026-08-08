import 'package:flutter/material.dart';

import 'iap_store.dart';
import 'strings.dart';

/// Grown-ups area: purchase, restore, diagnostics and privacy info.
/// Only reachable through the parental gate.
class PaywallScreen extends StatelessWidget {
  const PaywallScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      appBar: AppBar(
        title: Text(S.t('forGrownUps'),
            style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: ListenableBuilder(
        listenable: IapStore.instance,
        builder: (context, _) {
          final store = IapStore.instance;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Card(
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24)),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        store.owned
                            ? S.t('unlockedTitle')
                            : S.t('unlockTitle'),
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      if (!store.owned) ...[
                        Text(
                          S.t('benefits'),
                          style: const TextStyle(fontSize: 16, height: 1.6),
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          style: FilledButton.styleFrom(
                            minimumSize: const Size.fromHeight(56),
                            textStyle: const TextStyle(
                                fontSize: 18, fontWeight: FontWeight.w700),
                          ),
                          onPressed:
                              store.busy ? null : () => store.purchase(),
                          child: store.busy
                              ? const SizedBox(
                                  width: 26,
                                  height: 26,
                                  child: CircularProgressIndicator(
                                      strokeWidth: 3),
                                )
                              : Text(store.price.isEmpty
                                  ? S.t('unlockAll')
                                  : '${S.t('unlockAll')} - ${store.price}'),
                        ),
                        const SizedBox(height: 10),
                      ],
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size.fromHeight(52),
                        ),
                        onPressed: store.busy ? null : () => store.restore(),
                        child: Text(S.t('restore')),
                      ),
                      if (store.lastMessage.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(top: 12),
                          child: Text(
                            store.lastMessage,
                            style: const TextStyle(
                                fontSize: 15, fontWeight: FontWeight.w600),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24)),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(S.t('privacyTitle'),
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(fontWeight: FontWeight.w800)),
                      const SizedBox(height: 6),
                      const Text(
                        'This app collects no personal data. There are no '
                        'ads, no accounts, and no analytics. Drawings are '
                        'saved only on this device. The only online '
                        'feature is the Amazon Appstore purchase, handled '
                        'entirely by Amazon.',
                        style: TextStyle(fontSize: 15, height: 1.5),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24)),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(S.t('diagTitle'),
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(fontWeight: FontWeight.w800)),
                      const SizedBox(height: 6),
                      Text(
                        'Listener: ${store.listenerStatus}\n'
                        'Product: ${store.productStatus}\n'
                        'Owned: ${store.ownedStatus}',
                        style: const TextStyle(
                            fontSize: 14,
                            height: 1.6,
                            fontFamily: 'monospace'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
