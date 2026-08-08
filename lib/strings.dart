import 'dart:ui' as ui;

/// Tiny built-in localization for tier-1 country languages.
/// No internet, no packages — device locale decides the language.
class S {
  S._();

  static String get lang {
    final code = ui.PlatformDispatcher.instance.locale.languageCode;
    return _strings.containsKey(code) ? code : 'en';
  }

  static String t(String key) {
    final table = _strings[lang] ?? _strings['en']!;
    return table[key] ?? _strings['en']![key] ?? key;
  }

  /// Replaces %d placeholders in order.
  static String fmt(String template, List<int> args) {
    var out = template;
    for (final a in args) {
      out = out.replaceFirst('%d', '$a');
    }
    return out;
  }

  static String freeOf(int free, int total) =>
      fmt(t('freeOf'), [free, total]);

  static String freeHaveFun(int free) => fmt(t('freeHaveFun'), [free]);

  static String allUnlocked(int total) => fmt(t('allUnlocked'), [total]);

  static String whatIs(int a, int b) => fmt(t('whatIs'), [a, b]);

  static const Map<String, Map<String, String>> _strings = {
    'en': {
      'forGrownUps': 'For grown-ups',
      'gateTitle': 'Grown-ups only',
      'tryAgain': 'Try again!',
      'cancel': 'Cancel',
      'clear': 'Clear',
      'unlockAll': 'Unlock everything',
      'restore': 'Restore purchase',
      'freeOf': '%d free of %d',
      'freeHaveFun': '%d free pages - have fun!',
      'allUnlocked': 'All %d pages unlocked!',
      'unlockTitle': 'Unlock all 512 dino pages',
      'unlockedTitle': 'Everything is unlocked \u2714',
      'privacyTitle': 'Privacy',
      'diagTitle': 'Store diagnostics',
      'whatIs': 'What is %d \u00d7 %d?',
      'benefits': '\u2022 One-time purchase - no subscription\n'
          '\u2022 512 unique coloring pages, 8 categories\n'
          '\u2022 No ads, no internet needed, ever\n'
          '\u2022 Works for the whole family',
    },
    'de': {
      'forGrownUps': 'Für Erwachsene',
      'gateTitle': 'Nur für Erwachsene',
      'tryAgain': 'Nochmal!',
      'cancel': 'Abbrechen',
      'clear': 'Löschen',
      'unlockAll': 'Alles freischalten',
      'restore': 'Kauf wiederherstellen',
      'freeOf': '%d von %d kostenlos',
      'freeHaveFun': '%d kostenlose Seiten - viel Spaß!',
      'allUnlocked': 'Alle %d Seiten freigeschaltet!',
      'unlockTitle': 'Alle 512 Dino-Seiten freischalten',
      'unlockedTitle': 'Alles freigeschaltet \u2714',
      'privacyTitle': 'Datenschutz',
      'diagTitle': 'Store-Diagnose',
      'whatIs': 'Was ist %d \u00d7 %d?',
      'benefits': '\u2022 Einmaliger Kauf - kein Abo\n'
          '\u2022 512 einzigartige Ausmalbilder, 8 Kategorien\n'
          '\u2022 Keine Werbung, kein Internet nötig\n'
          '\u2022 Für die ganze Familie',
    },
    'fr': {
      'forGrownUps': 'Pour les adultes',
      'gateTitle': 'Réservé aux adultes',
      'tryAgain': 'Réessaie !',
      'cancel': 'Annuler',
      'clear': 'Effacer',
      'unlockAll': 'Tout débloquer',
      'restore': "Restaurer l'achat",
      'freeOf': '%d gratuites sur %d',
      'freeHaveFun': '%d pages gratuites - amuse-toi bien !',
      'allUnlocked': 'Les %d pages sont débloquées !',
      'unlockTitle': 'Débloquer les 512 pages de dinos',
      'unlockedTitle': 'Tout est débloqué \u2714',
      'privacyTitle': 'Confidentialité',
      'diagTitle': 'Diagnostic du store',
      'whatIs': 'Combien font %d \u00d7 %d ?',
      'benefits': "\u2022 Achat unique - pas d'abonnement\n"
          '\u2022 512 pages à colorier uniques, 8 catégories\n'
          '\u2022 Sans pub, sans Internet\n'
          '\u2022 Pour toute la famille',
    },
    'es': {
      'forGrownUps': 'Para adultos',
      'gateTitle': 'Solo para adultos',
      'tryAgain': '¡Inténtalo de nuevo!',
      'cancel': 'Cancelar',
      'clear': 'Borrar',
      'unlockAll': 'Desbloquear todo',
      'restore': 'Restaurar compra',
      'freeOf': '%d gratis de %d',
      'freeHaveFun': '%d páginas gratis - ¡diviértete!',
      'allUnlocked': '¡Las %d páginas desbloqueadas!',
      'unlockTitle': 'Desbloquear las 512 páginas de dinos',
      'unlockedTitle': 'Todo desbloqueado \u2714',
      'privacyTitle': 'Privacidad',
      'diagTitle': 'Diagnóstico de la tienda',
      'whatIs': '¿Cuánto es %d \u00d7 %d?',
      'benefits': '\u2022 Compra única - sin suscripción\n'
          '\u2022 512 páginas únicas para colorear, 8 categorías\n'
          '\u2022 Sin anuncios, sin Internet\n'
          '\u2022 Para toda la familia',
    },
    'it': {
      'forGrownUps': 'Per adulti',
      'gateTitle': 'Solo per adulti',
      'tryAgain': 'Riprova!',
      'cancel': 'Annulla',
      'clear': 'Cancella',
      'unlockAll': 'Sblocca tutto',
      'restore': 'Ripristina acquisto',
      'freeOf': '%d gratis su %d',
      'freeHaveFun': '%d pagine gratis - buon divertimento!',
      'allUnlocked': 'Tutte le %d pagine sbloccate!',
      'unlockTitle': 'Sblocca tutte le 512 pagine di dinosauri',
      'unlockedTitle': 'Tutto sbloccato \u2714',
      'privacyTitle': 'Privacy',
      'diagTitle': 'Diagnostica dello store',
      'whatIs': 'Quanto fa %d \u00d7 %d?',
      'benefits': '\u2022 Acquisto unico - nessun abbonamento\n'
          '\u2022 512 pagine da colorare uniche, 8 categorie\n'
          '\u2022 Niente pubblicità, niente Internet\n'
          '\u2022 Per tutta la famiglia',
    },
    'ja': {
      'forGrownUps': 'おとなのかたへ',
      'gateTitle': 'おとなの方専用',
      'tryAgain': 'もう一度！',
      'cancel': 'キャンセル',
      'clear': 'クリア',
      'unlockAll': 'すべてをアンロック',
      'restore': '購入を復元',
      'freeOf': '%d枚中%d枚無料',
      'freeHaveFun': '%dページ無料 - 楽しんでね！',
      'allUnlocked': '%dページすべて解放済み！',
      'unlockTitle': '512枚の恐竜ページをすべてアンロック',
      'unlockedTitle': 'すべて解放済み \u2714',
      'privacyTitle': 'プライバシー',
      'diagTitle': 'ストア診断',
      'whatIs': '%d \u00d7 %d は？',
      'benefits': '\u2022 買い切り - サブスクなし\n'
          '\u2022 512枚のユニークなぬりえ、8カテゴリー\n'
          '\u2022 広告なし、インターネット不要\n'
          '\u2022 家族みんなで遊べます',
    },
    'pt': {
      'forGrownUps': 'Para adultos',
      'gateTitle': 'Só para adultos',
      'tryAgain': 'Tente de novo!',
      'cancel': 'Cancelar',
      'clear': 'Limpar',
      'unlockAll': 'Desbloquear tudo',
      'restore': 'Restaurar compra',
      'freeOf': '%d grátis de %d',
      'freeHaveFun': '%d páginas grátis - divirta-se!',
      'allUnlocked': 'Todas as %d páginas desbloqueadas!',
      'unlockTitle': 'Desbloquear as 512 páginas de dinos',
      'unlockedTitle': 'Tudo desbloqueado \u2714',
      'privacyTitle': 'Privacidade',
      'diagTitle': 'Diagnóstico da loja',
      'whatIs': 'Quanto é %d \u00d7 %d?',
      'benefits': '\u2022 Compra única - sem assinatura\n'
          '\u2022 512 páginas exclusivas para colorir, 8 categorias\n'
          '\u2022 Sem anúncios, sem Internet\n'
          '\u2022 Para toda a família',
    },
  };
}
