import 'package:flutter/material.dart';

import 'progress_store.dart';

class _Tier {
  const _Tier(this.stars, this.title, this.emoji);

  final int stars;
  final String title;
  final String emoji;
}

const List<_Tier> kTiers = [
  _Tier(10, 'Dino Beginner', '\u{1F95A}'),
  _Tier(50, 'Dino Explorer', '\u{1F996}'),
  _Tier(150, 'Dino Artist', '\u{1F3A8}'),
  _Tier(300, 'Dino Champion', '\u{1F3C6}'),
  _Tier(520, 'DINO MASTER', '\u{1F451}'),
];

/// Star rewards screen: kids earn a star for every completed page.
class RewardsScreen extends StatelessWidget {
  const RewardsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF6E9),
      appBar: AppBar(
        title: const Text('My Stars \u{2B50}',
            style: TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: ListenableBuilder(
        listenable: ProgressStore.instance,
        builder: (context, _) {
          final stars = ProgressStore.instance.starCount;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Card(
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(24)),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      Text(
                        '\u{2B50} $stars',
                        style: Theme.of(context)
                            .textTheme
                            .displaySmall
                            ?.copyWith(fontWeight: FontWeight.w900),
                      ),
                      const SizedBox(height: 4),
                      Text('stars earned',
                          style: Theme.of(context).textTheme.titleMedium),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              for (final tier in kTiers) ...[
                _TierCard(tier: tier, stars: stars),
                const SizedBox(height: 10),
              ],
            ],
          );
        },
      ),
    );
  }
}

class _TierCard extends StatelessWidget {
  const _TierCard({required this.tier, required this.stars});

  final _Tier tier;
  final int stars;

  @override
  Widget build(BuildContext context) {
    final unlocked = stars >= tier.stars;
    final progress = (stars / tier.stars).clamp(0.0, 1.0);
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Text(
              unlocked ? tier.emoji : '\u{1F512}',
              style: const TextStyle(fontSize: 40),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    tier.title,
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 10,
                      backgroundColor: Colors.black12,
                      color: unlocked
                          ? const Color(0xFF43A047)
                          : const Color(0xFFFB8C00),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    unlocked
                        ? 'Unlocked!'
                        : '${tier.stars - stars} stars to go',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
