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
