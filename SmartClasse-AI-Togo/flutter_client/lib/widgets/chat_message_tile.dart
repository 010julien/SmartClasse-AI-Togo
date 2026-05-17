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
