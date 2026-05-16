import 'dart:convert';

import 'package:http/http.dart' as http;

class OrchestratorApi {
  static Future<Map<String, dynamic>> generateExercise(
    String baseUrl, {
    required String studentId,
    required String studentName,
    String level = 'CE1',
    String subject = 'math',
    String topic = 'fractions',
    String language = 'french',
  }) async {
    final uri = Uri.parse('$baseUrl/agents/orchestrator/generate');
    final body = {
      'student_id': studentId,
      'student_name': studentName,
      'level': level,
      'subject': subject,
      'topic': topic,
      'language': language,
    };

    final resp = await http
        .post(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 35));

    if (resp.statusCode < 200 || resp.statusCode >= 300) {
      throw Exception('API ${resp.statusCode}: ${resp.body}');
    }

    final decoded = jsonDecode(resp.body);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    throw Exception('Réponse API invalide');
  }
}
