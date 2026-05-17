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
      final msgs    = body['messages'] as List? ?? const [];
      final last    = msgs.isNotEmpty ? msgs.last as Map<String, dynamic> : <String, dynamic>{};
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
