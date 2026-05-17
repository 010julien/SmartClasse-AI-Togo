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
