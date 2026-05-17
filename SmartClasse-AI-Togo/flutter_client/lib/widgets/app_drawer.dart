import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../constants/colors.dart';

class AppDrawer extends StatelessWidget {
  final String language;
  final List<(String, String)> languages;
  final bool speak;
  final bool offlineDemo;
  final void Function(String) onLanguageChanged;
  final void Function(bool) onSpeakChanged;
  final void Function(bool) onOfflineDemoChanged;
  final VoidCallback onClearConversation;

  const AppDrawer({
    super.key,
    required this.language,
    required this.languages,
    required this.speak,
    required this.offlineDemo,
    required this.onLanguageChanged,
    required this.onSpeakChanged,
    required this.onOfflineDemoChanged,
    required this.onClearConversation,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(color: appGreen),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const CircleAvatar(
                  backgroundColor: appGold,
                  radius: 28,
                  child: Text(
                    'SC',
                    style: TextStyle(
                      color: appGreen,
                      fontWeight: FontWeight.bold,
                      fontSize: 20,
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'SmartClasse AI Togo',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'v0.1.0 · Gemma 4',
                  style: TextStyle(color: Colors.white.withAlpha(180), fontSize: 12),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              'LANGUE',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade600,
                letterSpacing: 1,
              ),
            ),
          ),
          ...languages.map((lang) => RadioListTile<String>(
            title: Text(lang.$2),
            value: lang.$1,
            groupValue: language,
            activeColor: appGreen,
            onChanged: (v) {
              onLanguageChanged(v!);
              Navigator.pop(context);
            },
          )),
          const Divider(),
          SwitchListTile(
            title: const Text('Réponse audio (TTS)'),
            subtitle: Text(
              kIsWeb
                  ? 'Non disponible sur navigateur web'
                  : 'Synthèse vocale des réponses',
            ),
            secondary: Icon(
              kIsWeb ? Icons.volume_off_outlined : Icons.volume_up_outlined,
              color: kIsWeb ? Colors.grey : appGreen,
            ),
            value: speak,
            activeColor: appGreen,
            onChanged: kIsWeb ? null : onSpeakChanged,
          ),
          SwitchListTile(
            title: const Text('Mode hors ligne'),
            subtitle: const Text('Réponses locales sans backend'),
            secondary: const Icon(Icons.wifi_off_outlined, color: appGreen),
            value: offlineDemo,
            activeColor: appGreen,
            onChanged: onOfflineDemoChanged,
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.delete_outline, color: Colors.red),
            title: const Text('Effacer la conversation'),
            onTap: () {
              onClearConversation();
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }
}
