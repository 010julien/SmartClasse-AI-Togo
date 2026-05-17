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
