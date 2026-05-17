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
