# Flutter SmartClasse — Restructuration en modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Éclater `lib/main.dart` (932 lignes, tout-en-un) en fichiers spécialisés sans modifier un seul comportement.

**Architecture:** Séparation en 4 couches — constants, models, services, widgets — avec une page (`chat_page.dart`) qui orchestre la logique d'état. `main.dart` ne garde que l'app shell et le thème.

**Tech Stack:** Flutter 3.x · Dart 3 · `record`, `audioplayers`, `http`, `path_provider`

---

## Structure cible

```
lib/
├── main.dart                      ← app shell + thème uniquement
├── constants/
│   └── colors.dart                ← 5 constantes de couleur
├── models/
│   ├── chat_message.dart          ← classe ChatMessage
│   └── agent_def.dart             ← classe AgentDef + liste agents
├── services/
│   ├── orchestrator_api.dart      ← INCHANGÉ (déjà extrait)
│   └── api_service.dart           ← HTTP post + réponses offline
├── pages/
│   └── chat_page.dart             ← ChatPage + _ChatPageState (logique)
└── widgets/
    ├── loading_bar.dart
    ├── chat_message_tile.dart
    ├── chat_message_list.dart
    ├── agent_bar.dart
    ├── app_drawer.dart
    └── input_bar.dart
```

---

### Tâche 1 : Créer `lib/constants/colors.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/constants/colors.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';

const appGreen      = Color(0xFF006A4E);
const appGold       = Color(0xFFFFCE00);
const appGreenLight = Color(0xFFE6F4F0);
const appGoldLight  = Color(0xFFFFF9E0);
const appSurface    = Color(0xFFF4F7F6);
```

- [ ] **Étape 2 : Vérifier que le fichier est valide (aucune dépendance manquante)**

```bash
cd SmartClasse-AI-Togo/flutter_client
flutter analyze lib/constants/colors.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/constants/colors.dart
git commit -m "refactor(flutter): extract color constants to lib/constants/colors.dart"
```

---

### Tâche 2 : Créer `lib/models/chat_message.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/models/chat_message.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
class ChatMessage {
  final String role;
  final String text;
  final String? audioUrl;
  final DateTime timestamp;

  ChatMessage({
    required this.role,
    required this.text,
    this.audioUrl,
  }) : timestamp = DateTime.now();
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/models/chat_message.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/models/chat_message.dart
git commit -m "refactor(flutter): extract ChatMessage model"
```

---

### Tâche 3 : Créer `lib/models/agent_def.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/models/agent_def.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';
import '../constants/colors.dart';

class AgentDef {
  final String id;
  final String label;
  final IconData icon;
  final Color color;

  const AgentDef({
    required this.id,
    required this.label,
    required this.icon,
    required this.color,
  });
}

const agents = <AgentDef>[
  AgentDef(id: 'diagnostix', label: 'DIAGNOSTIX', icon: Icons.medical_information_outlined, color: Color(0xFF1976D2)),
  AgentDef(id: 'pilotix',    label: 'PILOTIX',    icon: Icons.dashboard_outlined,            color: Color(0xFF388E3C)),
  AgentDef(id: 'equitix',    label: 'EQUITIX',    icon: Icons.volunteer_activism_outlined,   color: Color(0xFFE64A19)),
  AgentDef(id: 'parentix',   label: 'PARENTIX',   icon: Icons.sms_outlined,                 color: Color(0xFF7B1FA2)),
  AgentDef(id: 'orchestrator', label: 'ORCHESTRATOR', icon: Icons.auto_awesome_outlined,    color: appGreen),
];
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/models/agent_def.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/models/agent_def.dart
git commit -m "refactor(flutter): extract AgentDef model and agents list"
```

---

### Tâche 4 : Créer `lib/services/api_service.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/services/api_service.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;

  const ApiService({required this.baseUrl});

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    final response = await http
        .post(
          Uri.parse('$baseUrl$path'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 600));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('API ${response.statusCode}: ${response.body}');
    }
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) return decoded;
    throw Exception('Réponse API invalide');
  }

  static Map<String, dynamic> offlineResponse(String path, Map<String, dynamic> body) {
    if (path == '/agents/linguix/chat') {
      final msgs = body['messages'] as List? ?? const [];
      final last = msgs.isNotEmpty ? msgs.last as Map<String, dynamic> : <String, dynamic>{};
      final content = (last['content'] as String?) ?? '';
      return {
        'status': 'success',
        'result': {
          'assistant_text': 'Mode hors ligne — reçu : "$content"',
          'audio_url': null,
        },
      };
    }
    if (path == '/agents/diagnostix/analyze') {
      return {
        'status': 'success',
        'analysis': {
          'teacher_message': "Mode hors ligne : Akouvi a besoin d'un diagnostic réel.",
          'next_action': 'Lancer les exercices de diagnostic dès la reconnexion.',
          'retroactive_exercise': {
            'title': 'Rattrapage hors ligne',
            'problem': 'Akouvi partage 8 sacs de sorgho et en garde 3. Combien partent au marché ?',
          },
        },
      };
    }
    if (path == '/agents/pilotix/dashboard') {
      return {
        'status': 'success',
        'dashboard': {
          'class_overview': {'ready_count': 23, 'support_count': 18, 'average_readiness': 57.0},
          'lesson_suggestion': {
            'class_message': "23 élèves prêts. 18 ont besoin d'un cours différencié.",
            'teacher_voice_prompt': 'Kossi, lancez une activité en deux groupes.',
            'audio': {'audio_url': null},
          },
        },
      };
    }
    if (path == '/agents/equitix/risk_assessment') {
      return {
        'status': 'success',
        'assessment': {
          'risk_level': 'moderate',
          'teacher_action': 'Contacter la famille et alléger la charge scolaire.',
          'voice_alert': {'audio_url': null},
        },
      };
    }
    if (path == '/agents/parentix/send_sms') {
      return {
        'status': 'success',
        'sms': {
          'status': 'dry_run',
          'weekly_message': {'sms_text': 'Mode hors ligne : SMS prêt pour envoi.'},
        },
      };
    }
    return {'status': 'success'};
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/services/api_service.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/services/api_service.dart
git commit -m "refactor(flutter): extract ApiService with HTTP post and offline responses"
```

---

### Tâche 5 : Créer `lib/widgets/loading_bar.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/loading_bar.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';
import '../constants/colors.dart';

class LoadingBar extends StatelessWidget {
  final String? activeAgent;

  const LoadingBar({super.key, this.activeAgent});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: appGreenLight,
      child: Row(
        children: [
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(appGreen),
            ),
          ),
          const SizedBox(width: 10),
          Text(
            activeAgent != null ? '$activeAgent en cours...' : 'Chargement...',
            style: const TextStyle(fontSize: 13, color: appGreen, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/loading_bar.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/loading_bar.dart
git commit -m "refactor(flutter): extract LoadingBar widget"
```

---

### Tâche 6 : Créer `lib/widgets/chat_message_tile.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/chat_message_tile.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';
import '../constants/colors.dart';
import '../models/chat_message.dart';

class ChatMessageTile extends StatelessWidget {
  final ChatMessage message;
  final void Function(String) onPlayAudio;

  const ChatMessageTile({
    super.key,
    required this.message,
    required this.onPlayAudio,
  });

  @override
  Widget build(BuildContext context) {
    final isUser   = message.role == 'user';
    final isSystem = message.role == 'system';

    if (isSystem) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.orange.shade50,
              border: Border.all(color: Colors.orange.shade200),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              message.text,
              style: TextStyle(fontSize: 12, color: Colors.orange.shade800),
            ),
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: appGreenLight,
              child: const Text(
                'AI',
                style: TextStyle(fontSize: 10, color: appGreen, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: isUser ? appGreen : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft:     const Radius.circular(18),
                      topRight:    const Radius.circular(18),
                      bottomLeft:  Radius.circular(isUser ? 18 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 18),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withAlpha(13),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Text(
                    message.text,
                    style: TextStyle(
                      color: isUser ? Colors.white : Colors.black87,
                      fontSize: 14,
                      height: 1.4,
                    ),
                  ),
                ),
                if (message.audioUrl != null && message.audioUrl!.isNotEmpty)
                  TextButton.icon(
                    style: TextButton.styleFrom(
                      foregroundColor: appGreen,
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                    ),
                    onPressed: () => onPlayAudio(message.audioUrl!),
                    icon: const Icon(Icons.play_circle_outline, size: 18),
                    label: const Text('Écouter', style: TextStyle(fontSize: 12)),
                  ),
                Padding(
                  padding: const EdgeInsets.only(top: 2, left: 4, right: 4),
                  child: Text(
                    '${message.timestamp.hour.toString().padLeft(2, '0')}:'
                    '${message.timestamp.minute.toString().padLeft(2, '0')}',
                    style: TextStyle(fontSize: 10, color: Colors.grey.shade500),
                  ),
                ),
              ],
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: appGoldLight,
              child: const Icon(Icons.person_outline, size: 16, color: appGreen),
            ),
          ],
        ],
      ),
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/chat_message_tile.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/chat_message_tile.dart
git commit -m "refactor(flutter): extract ChatMessageTile widget"
```

---

### Tâche 7 : Créer `lib/widgets/chat_message_list.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/chat_message_list.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';
import '../constants/colors.dart';
import '../models/chat_message.dart';
import 'chat_message_tile.dart';

class ChatMessageList extends StatelessWidget {
  final List<ChatMessage> messages;
  final ScrollController scrollController;
  final void Function(String) onPlayAudio;

  const ChatMessageList({
    super.key,
    required this.messages,
    required this.scrollController,
    required this.onPlayAudio,
  });

  @override
  Widget build(BuildContext context) {
    if (messages.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: const BoxDecoration(color: appGreenLight, shape: BoxShape.circle),
              child: const Icon(Icons.school_outlined, size: 40, color: appGreen),
            ),
            const SizedBox(height: 16),
            const Text(
              'Bienvenue sur SmartClasse',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: appGreen),
            ),
            const SizedBox(height: 8),
            Text(
              'Écrivez un message ou sélectionnez un agent ci-dessus.',
              style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      controller: scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemCount: messages.length,
      itemBuilder: (context, index) => ChatMessageTile(
        message: messages[index],
        onPlayAudio: onPlayAudio,
      ),
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/chat_message_list.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/chat_message_list.dart
git commit -m "refactor(flutter): extract ChatMessageList widget"
```

---

### Tâche 8 : Créer `lib/widgets/agent_bar.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/agent_bar.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/material.dart';
import '../models/agent_def.dart';

class AgentBar extends StatelessWidget {
  final List<AgentDef> agentList;
  final String? activeAgent;
  final bool loading;
  final void Function(String) onAgentTap;

  const AgentBar({
    super.key,
    required this.agentList,
    required this.activeAgent,
    required this.loading,
    required this.onAgentTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      color: Colors.white,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: agentList.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, i) {
          final agent    = agentList[i];
          final isActive = activeAgent == agent.id.toUpperCase() ||
                           activeAgent == agent.label;
          return FilledButton.tonalIcon(
            style: FilledButton.styleFrom(
              backgroundColor: isActive ? agent.color : agent.color.withAlpha(24),
              foregroundColor: isActive ? Colors.white : agent.color,
              padding: const EdgeInsets.symmetric(horizontal: 14),
              visualDensity: VisualDensity.compact,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
            onPressed: loading ? null : () => onAgentTap(agent.id),
            icon: Icon(agent.icon, size: 16),
            label: Text(
              agent.label,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
          );
        },
      ),
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/agent_bar.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/agent_bar.dart
git commit -m "refactor(flutter): extract AgentBar widget"
```

---

### Tâche 9 : Créer `lib/widgets/app_drawer.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/app_drawer.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
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
            subtitle: const Text('Synthèse vocale des réponses'),
            secondary: const Icon(Icons.volume_up_outlined, color: appGreen),
            value: speak,
            activeColor: appGreen,
            onChanged: onSpeakChanged,
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
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/app_drawer.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/app_drawer.dart
git commit -m "refactor(flutter): extract AppDrawer widget"
```

---

### Tâche 10 : Créer `lib/widgets/input_bar.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/widgets/input_bar.dart`

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/colors.dart';

class InputBar extends StatelessWidget {
  final TextEditingController controller;
  final bool loading;
  final bool isRecording;
  final String language;
  final AnimationController micPulseController;
  final VoidCallback onSend;
  final VoidCallback onToggleRecording;

  const InputBar({
    super.key,
    required this.controller,
    required this.loading,
    required this.isRecording,
    required this.language,
    required this.micPulseController,
    required this.onSend,
    required this.onToggleRecording,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(13),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Focus(
              onKeyEvent: (node, event) {
                if (event is KeyDownEvent &&
                    event.logicalKey == LogicalKeyboardKey.enter &&
                    !HardwareKeyboard.instance.isShiftPressed) {
                  onSend();
                  return KeyEventResult.handled;
                }
                return KeyEventResult.ignored;
              },
              child: TextField(
                controller: controller,
                minLines: 1,
                maxLines: 4,
                textInputAction: TextInputAction.send,
                decoration: InputDecoration(
                  hintText: 'Écrire en $language... (Entrée pour envoyer)',
                  hintStyle: TextStyle(color: Colors.grey.shade400),
                  isDense: true,
                ),
                onSubmitted: (_) => onSend(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          Material(
            color: appGreen,
            borderRadius: BorderRadius.circular(24),
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: loading ? null : onSend,
              child: const Padding(
                padding: EdgeInsets.all(12),
                child: Icon(Icons.send_rounded, color: Colors.white, size: 20),
              ),
            ),
          ),
          if (!kIsWeb) ...[
            const SizedBox(width: 8),
            AnimatedBuilder(
              animation: micPulseController,
              builder: (context, child) {
                return Material(
                  color: isRecording
                      ? Color.lerp(
                          Colors.red.shade600,
                          Colors.red.shade400,
                          micPulseController.value,
                        )!
                      : appGreenLight,
                  borderRadius: BorderRadius.circular(24),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(24),
                    onTap: loading ? null : onToggleRecording,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Icon(
                        isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                        color: isRecording ? Colors.white : appGreen,
                        size: 20,
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        ],
      ),
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/widgets/input_bar.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/widgets/input_bar.dart
git commit -m "refactor(flutter): extract InputBar widget"
```

---

### Tâche 11 : Créer `lib/pages/chat_page.dart`

**Fichiers :**
- Créer : `SmartClasse-AI-Togo/flutter_client/lib/pages/chat_page.dart`

> Contient `ChatPage` et `_ChatPageState` avec toute la logique métier (agents, API, audio). Les `_buildXxx` qui retournent des widgets tiers sont remplacés par les nouvelles classes. Seul `_buildAppBar` reste inline (trop couplé à `_offlineDemo`).

- [ ] **Étape 1 : Créer le fichier**

```dart
import 'dart:convert';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

import '../constants/colors.dart';
import '../models/agent_def.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';
import '../services/orchestrator_api.dart';
import '../widgets/agent_bar.dart';
import '../widgets/app_drawer.dart';
import '../widgets/chat_message_list.dart';
import '../widgets/input_bar.dart';
import '../widgets/loading_bar.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> with TickerProviderStateMixin {
  final _inputController  = TextEditingController();
  final _scrollController = ScrollController();
  final _player           = AudioPlayer();
  final _messages         = <ChatMessage>[];

  late final AudioRecorder _recorder;
  bool _recorderReady = false;

  bool    _loading     = false;
  bool    _isRecording = false;
  bool    _speak       = false;
  bool    _offlineDemo = false;
  String  _language    = 'french';
  String? _activeAgent;
  late final String _sessionId;

  late final AnimationController _micPulseController;
  late final ApiService          _apiService;

  final _demoStudentId   = 'demo-1';
  final _demoStudentName = 'Akouvi';
  final _demoTeacherName = 'Kossi';
  final _demoClassName   = 'CM1 A';

  final _languages = const [
    ('french',  'Français'),
    ('kabyie',  'Kabiyè'),
    ('ewe',     'Ewe'),
    ('haoussa', 'Haoussa'),
    ('mina',    'Mina'),
    ('tem',     'Tem'),
  ];

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    _sessionId = 'session_${DateTime.now().millisecondsSinceEpoch.toRadixString(36)}';
    _micPulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);

    _apiService = ApiService(baseUrl: _baseUrl);

    if (!kIsWeb) {
      _recorder      = AudioRecorder();
      _recorderReady = true;
    }
  }

  String get _baseUrl {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    return defaultTargetPlatform == TargetPlatform.android
        ? 'http://10.0.2.2:8000'
        : 'http://127.0.0.1:8000';
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    _micPulseController.dispose();
    if (_recorderReady) _recorder.dispose();
    _player.dispose();
    super.dispose();
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _addMessage(ChatMessage msg) {
    setState(() => _messages.add(msg));
    _scrollToBottom();
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    if (_offlineDemo) return ApiService.offlineResponse(path, body);
    return _apiService.post(path, body);
  }

  List<Map<String, String>> _buildChatHistory() {
    final history = <Map<String, String>>[];
    for (final msg in _messages) {
      if (msg.role != 'user' && msg.role != 'assistant') continue;
      if (msg.text.isEmpty) continue;
      if (msg.role == 'assistant') {
        if (msg.text.length < 5) continue;
        if (msg.text.startsWith('📱')) continue;
      }
      history.add({'role': msg.role, 'content': msg.text});
    }
    if (history.length > 6) return history.sublist(history.length - 6);
    return history;
  }

  // ── Actions utilisateur ────────────────────────────────────────────────────

  Future<void> _sendText() async {
    final text = _inputController.text.trim();
    if (text.isEmpty || _loading) return;
    _addMessage(ChatMessage(role: 'user', text: text));
    setState(() {
      _loading     = true;
      _activeAgent = 'LINGUIX';
      _inputController.clear();
    });

    try {
      final chatHistory = _buildChatHistory()
        ..removeWhere((m) => m['content']?.isEmpty ?? true);

      final result = await _postJson('/agents/linguix/chat', {
        'messages':   chatHistory,
        'speak':      _speak,
        'language':   _language,
        'user_level': 'CE1',
        'session_id': _sessionId,
        'user_name':  _demoStudentName,
      });
      final payload       = result['result'] as Map<String, dynamic>? ?? {};
      final assistantText = (payload['assistant_text'] as String?) ?? 'Aucune réponse';
      final audioUrl      = payload['audio_url'] as String?;
      _addMessage(ChatMessage(role: 'assistant', text: assistantText, audioUrl: audioUrl));
      if (audioUrl != null && audioUrl.isNotEmpty) await _playServerAudio(audioUrl);
    } catch (e) {
      if (!_offlineDemo) {
        setState(() => _offlineDemo = true);
        _addMessage(ChatMessage(
          role: 'system',
          text: 'Erreur : $e\n\nBackend indisponible. Mode hors ligne activé.',
        ));
        _addMessage(ChatMessage(role: 'assistant', text: 'Mode hors ligne — reçu : "$text"'));
      } else {
        _addMessage(ChatMessage(role: 'assistant', text: 'Mode hors ligne — reçu : "$text"'));
      }
    } finally {
      if (mounted) setState(() { _loading = false; _activeAgent = null; });
    }
  }

  Future<void> _toggleRecording() async {
    if (_loading || !_recorderReady) return;

    if (_isRecording) {
      final path = await _recorder.stop();
      setState(() => _isRecording = false);
      if (path == null || path.isEmpty) return;
      await _sendVoice(path);
      return;
    }

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      _addMessage(ChatMessage(role: 'system', text: 'Permission microphone refusée.'));
      return;
    }

    final tempDir  = await getTemporaryDirectory();
    final filePath = '${tempDir.path}/smartclasse_${DateTime.now().millisecondsSinceEpoch}.wav';
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000, numChannels: 1),
      path: filePath,
    );
    setState(() => _isRecording = true);
  }

  Future<void> _sendVoice(String path) async {
    _addMessage(ChatMessage(role: 'user', text: '🎤 Message vocal envoyé'));
    setState(() { _loading = true; _activeAgent = 'LINGUIX Voice'; });

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl/agents/linguix/voice_pipeline'),
      );
      request.fields['source_language_hint'] = _language;
      request.fields['target_languages']      = 'ewe,kabyie';
      request.files.add(await http.MultipartFile.fromPath('file', path));

      final streamed = await request.send().timeout(const Duration(seconds: 70));
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        final decoded      = jsonDecode(response.body) as Map<String, dynamic>;
        final pipeline     = decoded['pipeline'] as Map<String, dynamic>? ?? {};
        final transcription = pipeline['transcription'] as Map<String, dynamic>? ?? {};
        final transcriptionText = (transcription['text'] as String?) ?? '';
        String  reply      = 'Transcription : $transcriptionText';
        String? firstAudio;
        final translations = pipeline['translations'];
        if (translations is List && translations.isNotEmpty) {
          final first = translations.first;
          if (first is Map<String, dynamic>) {
            final txt   = first['translated_instruction'] as String?;
            final audio = first['audio'];
            if (txt != null && txt.isNotEmpty) reply = txt;
            if (audio is Map<String, dynamic>) firstAudio = audio['audio_url'] as String?;
          }
        }
        _addMessage(ChatMessage(role: 'assistant', text: reply, audioUrl: firstAudio));
        if (firstAudio != null && firstAudio.isNotEmpty) await _playServerAudio(firstAudio);
      } else {
        _addMessage(ChatMessage(role: 'system', text: 'Erreur API voice : ${response.statusCode}'));
      }
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur upload vocal : $e'));
    } finally {
      if (mounted) setState(() { _loading = false; _activeAgent = null; });
    }
  }

  Future<void> _playServerAudio(String audioUrl) async {
    final cleaned = audioUrl.startsWith('/') ? audioUrl : '/$audioUrl';
    await _player.play(UrlSource('$_baseUrl$cleaned'));
  }

  // ── Actions agents ─────────────────────────────────────────────────────────

  Future<void> _runAgent(String agentId) async {
    if (_loading) return;
    setState(() { _loading = true; _activeAgent = agentId.toUpperCase(); });

    try {
      switch (agentId) {
        case 'diagnostix':  await _runDiagnostix();
        case 'pilotix':     await _runPilotix();
        case 'equitix':     await _runEquitix();
        case 'parentix':    await _runParentix();
        case 'orchestrator': await _runOrchestrator();
      }
    } finally {
      if (mounted) setState(() { _loading = false; _activeAgent = null; });
    }
  }

  Future<void> _runDiagnostix() async {
    try {
      final result   = await _postJson('/agents/diagnostix/analyze', {
        'student_id':   _demoStudentId,
        'student_name': _demoStudentName,
        'level':        'CM1',
        'language':     _language,
      });
      final analysis      = result['analysis'] as Map<String, dynamic>? ?? {};
      final teacherMessage = (analysis['teacher_message'] as String?) ?? 'DIAGNOSTIX prêt.';
      final nextAction    = (analysis['next_action'] as String?) ?? '';
      final retro         = analysis['retroactive_exercise'] as Map<String, dynamic>?;
      final buf           = StringBuffer('📊 DIAGNOSTIX\n$teacherMessage');
      if (nextAction.isNotEmpty) buf.writeln('\n→ $nextAction');
      if (retro != null) {
        final title   = retro['title'] as String?;
        final problem = retro['problem'] as String?;
        if (title != null)   buf.writeln('\n📝 $title');
        if (problem != null) buf.writeln(problem);
      }
      _addMessage(ChatMessage(role: 'assistant', text: buf.toString().trim()));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur DIAGNOSTIX : $e'));
    }
  }

  Future<void> _runPilotix() async {
    try {
      final result     = await _postJson('/agents/pilotix/dashboard', {
        'teacher_name': _demoTeacherName,
        'class_name':   _demoClassName,
        'student_ids':  [_demoStudentId],
        'language':     _language,
      });
      final dashboard  = result['dashboard'] as Map<String, dynamic>? ?? {};
      final overview   = dashboard['class_overview'] as Map<String, dynamic>? ?? {};
      final suggestion = dashboard['lesson_suggestion'] as Map<String, dynamic>? ?? {};
      final classMessage  = (suggestion['class_message'] as String?) ?? 'PILOTIX prêt.';
      final voicePrompt   = (suggestion['teacher_voice_prompt'] as String?) ?? '';
      final audioUrl      = (suggestion['audio'] as Map<String, dynamic>?)?['audio_url'] as String?;
      _addMessage(ChatMessage(
        role: 'assistant',
        text: '🏫 PILOTIX — $_demoClassName\n$classMessage\n'
              '✅ Prêts : ${overview['ready_count'] ?? 0} | '
              '🆘 Soutien : ${overview['support_count'] ?? 0}\n'
              '👨‍🏫 $voicePrompt',
        audioUrl: audioUrl,
      ));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur PILOTIX : $e'));
    }
  }

  Future<void> _runEquitix() async {
    try {
      final result     = await _postJson('/agents/equitix/risk_assessment', {
        'student_id':   _demoStudentId,
        'student_name': _demoStudentName,
        'language':     _language,
        'signals': {
          'attendance_days_missed': 4,
          'participation_score':    30,
          'missing_assignments':    3,
        },
      });
      final assessment   = result['assessment'] as Map<String, dynamic>? ?? {};
      final riskLevel    = (assessment['risk_level'] as String?) ?? 'unknown';
      final teacherAction = (assessment['teacher_action'] as String?) ?? '';
      final audioUrl     = (assessment['voice_alert'] as Map<String, dynamic>?)?['audio_url'] as String?;
      final emoji        = riskLevel == 'high' ? '🔴' : riskLevel == 'moderate' ? '🟡' : '🟢';
      _addMessage(ChatMessage(
        role: 'assistant',
        text: '$emoji EQUITIX — $_demoStudentName\nRisque : $riskLevel\n📋 $teacherAction',
        audioUrl: audioUrl,
      ));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur EQUITIX : $e'));
    }
  }

  Future<void> _runParentix() async {
    try {
      final result = await _postJson('/agents/parentix/send_sms', {
        'student_id':   _demoStudentId,
        'student_name': _demoStudentName,
        'phone_number': '',
        'language':     _language,
        'dry_run':      true,
      });
      final sms    = result['sms'] as Map<String, dynamic>? ?? {};
      final weekly = sms['weekly_message'] as Map<String, dynamic>? ?? {};
      final text   = (weekly['sms_text'] as String?) ?? 'SMS généré.';
      _addMessage(ChatMessage(role: 'assistant', text: '📱 PARENTIX\n$text'));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur PARENTIX : $e'));
    }
  }

  Future<void> _runOrchestrator() async {
    try {
      final exerciseResp = await OrchestratorApi.generateExercise(
        _baseUrl,
        studentId:   _demoStudentId,
        studentName: _demoStudentName,
        level:       'CE1',
        subject:     'math',
        topic:       'fractions',
        language:    _language,
      );
      final exercise = exerciseResp['exercise'] as Map<String, dynamic>?;
      if (exercise != null) {
        final title   = (exercise['title'] as String?) ?? 'Exercice';
        final problem = (exercise['problem'] as String?) ?? '';
        _addMessage(ChatMessage(role: 'assistant', text: '✨ ORCHESTRATOR\n📝 $title\n$problem'));
      } else {
        _addMessage(ChatMessage(role: 'assistant', text: 'ORCHESTRATOR : réponse vide.'));
      }
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur ORCHESTRATOR : $e'));
    }
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: appSurface,
      appBar: _buildAppBar(),
      drawer: AppDrawer(
        language:              _language,
        languages:             _languages,
        speak:                 _speak,
        offlineDemo:           _offlineDemo,
        onLanguageChanged:     (v) => setState(() => _language    = v),
        onSpeakChanged:        (v) => setState(() => _speak       = v),
        onOfflineDemoChanged:  (v) => setState(() => _offlineDemo = v),
        onClearConversation:   ()  => setState(() => _messages.clear()),
      ),
      body: SafeArea(
        child: Column(
          children: [
            AgentBar(
              agentList:   agents,
              activeAgent: _activeAgent,
              loading:     _loading,
              onAgentTap:  _runAgent,
            ),
            Expanded(
              child: ChatMessageList(
                messages:         _messages,
                scrollController: _scrollController,
                onPlayAudio:      _playServerAudio,
              ),
            ),
            if (_loading) LoadingBar(activeAgent: _activeAgent),
            InputBar(
              controller:          _inputController,
              loading:             _loading,
              isRecording:         _isRecording,
              language:            _language,
              micPulseController:  _micPulseController,
              onSend:              _sendText,
              onToggleRecording:   _toggleRecording,
            ),
          ],
        ),
      ),
    );
  }

  AppBar _buildAppBar() {
    return AppBar(
      title: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('SmartClasse AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          Text('Togo · Éducation adaptative', style: TextStyle(fontSize: 11, color: Colors.white70)),
        ],
      ),
      actions: [
        Container(
          margin:  const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: _offlineDemo ? Colors.orange.shade700 : const Color(0xFF00C853),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _offlineDemo ? 'HORS LIGNE' : 'EN LIGNE',
            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ),
      ],
    );
  }
}
```

- [ ] **Étape 2 : Analyser**

```bash
flutter analyze lib/pages/chat_page.dart
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Commit**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/pages/chat_page.dart
git commit -m "refactor(flutter): extract ChatPage to lib/pages/chat_page.dart"
```

---

### Tâche 12 : Réécrire `lib/main.dart`

**Fichiers :**
- Modifier : `SmartClasse-AI-Togo/flutter_client/lib/main.dart`

> `main.dart` ne garde que `SmartClasseApp` (app shell + thème). La logique est déléguée à `ChatPage`.

- [ ] **Étape 1 : Remplacer le contenu intégral de `main.dart`**

```dart
import 'package:flutter/material.dart';
import 'constants/colors.dart';
import 'pages/chat_page.dart';

void main() {
  runApp(const SmartClasseApp());
}

class SmartClasseApp extends StatelessWidget {
  const SmartClasseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartClasse AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: appGreen,
          primary:   appGreen,
          secondary: appGold,
          surface:   appSurface,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: appGreen,
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: false,
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
            borderSide: BorderSide(color: Colors.grey.shade300),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
            borderSide: BorderSide(color: Colors.grey.shade300),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24),
            borderSide: const BorderSide(color: appGreen, width: 2),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        ),
      ),
      home: const ChatPage(),
    );
  }
}
```

- [ ] **Étape 2 : Analyser l'ensemble du projet**

```bash
cd SmartClasse-AI-Togo/flutter_client
flutter analyze
```
Attendu : `No issues found!`

- [ ] **Étape 3 : Vérifier que l'appli compile**

```bash
flutter build apk --debug
# ou sur desktop :
flutter build windows --debug
```
Attendu : build terminé sans erreur.

- [ ] **Étape 4 : Commit final**

```bash
git add SmartClasse-AI-Togo/flutter_client/lib/main.dart
git commit -m "refactor(flutter): simplify main.dart to app shell only — split complete"
```
