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
          primary: appGreen,
          secondary: appGold,
          surface: appSurface,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: appGreen,
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: false,
        ),
        cardTheme: CardThemeData(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
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
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 14,
          ),
        ),
      ),
      home: const ChatPage(),
    );
  }
}

// ─── Modèle de message ────────────────────────────────────────────────────

class ChatMessage {
  final String role;
  final String text;
  final String? audioUrl;
  final DateTime timestamp;

  ChatMessage({required this.role, required this.text, this.audioUrl})
    : timestamp = DateTime.now();
}

// ─── Définition des agents ────────────────────────────────────────────────

class _AgentDef {
  final String id;
  final String label;
  final IconData icon;
  final Color color;

  const _AgentDef({
    required this.id,
    required this.label,
    required this.icon,
    required this.color,
  });
}

const _agents = [
  _AgentDef(
    id: 'diagnostix',
    label: 'DIAGNOSTIX',
    icon: Icons.medical_information_outlined,
    color: Color(0xFF1976D2),
  ),
  _AgentDef(
    id: 'pilotix',
    label: 'PILOTIX',
    icon: Icons.dashboard_outlined,
    color: Color(0xFF388E3C),
  ),
  _AgentDef(
    id: 'equitix',
    label: 'EQUITIX',
    icon: Icons.volunteer_activism_outlined,
    color: Color(0xFFE64A19),
  ),
  _AgentDef(
    id: 'parentix',
    label: 'PARENTIX',
    icon: Icons.sms_outlined,
    color: Color(0xFF7B1FA2),
  ),
  _AgentDef(
    id: 'orchestrator',
    label: 'ORCHESTRATOR',
    icon: Icons.auto_awesome_outlined,
    color: _green,
  ),
];

// ─── Page principale ──────────────────────────────────────────────────────

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> with TickerProviderStateMixin {
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();
  final _player = AudioPlayer();
  final _messages = <ChatMessage>[];

  late final AudioRecorder _recorder;
  bool _recorderReady = false;

  bool _loading = false;
  bool _isRecording = false;
  bool _speak = false;
  bool _offlineDemo = false;
  String _language = 'french';
  String? _recordFile;
  String? _activeAgent;

  late final AnimationController _micPulseController;

  final _demoStudentId = 'demo-1';
  final _demoStudentName = 'Akouvi';
  final _demoTeacherName = 'Kossi';
  final _demoClassName = 'CM1 A';

  final _languages = const [
    ('french', 'Français'),
    ('kabyie', 'Kabiyè'),
    ('ewe', 'Ewe'),
    ('haoussa', 'Haoussa'),
    ('mina', 'Mina'),
    ('tem', 'Tem'),
  ];

  @override
  void initState() {
    super.initState();
    _micPulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);

    if (!kIsWeb) {
      _recorder = AudioRecorder();
      _recorderReady = true;
    }
  }

  String get _baseUrl {
    if (kIsWeb) return 'http://127.0.0.1:8010';
    return defaultTargetPlatform == TargetPlatform.android
        ? 'http://10.0.2.2:8010'
        : 'http://127.0.0.1:8010';
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

  // ── Requêtes API ────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    if (_offlineDemo) return _offlineJson(path, body);

    final response = await http
        .post(
          Uri.parse('$_baseUrl$path'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 35));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('API ${response.statusCode}: ${response.body}');
    }
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) return decoded;
    throw Exception('Réponse API invalide');
  }

  Map<String, dynamic> _offlineJson(String path, Map<String, dynamic> body) {
    if (path == '/agents/linguix/chat') {
      final msgs = body['messages'] as List? ?? const [];
      final last = msgs.isNotEmpty
          ? msgs.last as Map<String, dynamic>
          : <String, dynamic>{};
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
          'teacher_message':
              'Mode hors ligne : Akouvi a besoin d\'un diagnostic réel.',
          'next_action':
              'Lancer les exercices de diagnostic dès la reconnexion.',
          'retroactive_exercise': {
            'title': 'Rattrapage hors ligne',
            'problem':
                'Akouvi partage 8 sacs de sorgho et en garde 3. Combien partent au marché ?',
          },
        },
      };
    }
    if (path == '/agents/pilotix/dashboard') {
      return {
        'status': 'success',
        'dashboard': {
          'class_overview': {
            'ready_count': 23,
            'support_count': 18,
            'average_readiness': 57.0,
          },
          'lesson_suggestion': {
            'class_message':
                '23 élèves prêts. 18 ont besoin d\'un cours différencié.',
            'teacher_voice_prompt':
                'Kossi, lancez une activité en deux groupes.',
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
          'teacher_action':
              'Contacter la famille et alléger la charge scolaire.',
          'voice_alert': {'audio_url': null},
        },
      };
    }
    if (path == '/agents/parentix/send_sms') {
      return {
        'status': 'success',
        'sms': {
          'status': 'dry_run',
          'weekly_message': {
            'sms_text': 'Mode hors ligne : SMS prêt pour envoi.',
          },
        },
      };
    }
    return {'status': 'success'};
  }

  // ── Actions utilisateur ─────────────────────────────────────────────────

  Future<void> _sendText() async {
    final text = _inputController.text.trim();
    if (text.isEmpty || _loading) return;
    _addMessage(ChatMessage(role: 'user', text: text));
    setState(() {
      _loading = true;
      _activeAgent = 'LINGUIX';
      _inputController.clear();
    });

    try {
      final result = await _postJson('/agents/linguix/chat', {
        'messages': [
          {'role': 'user', 'content': text},
        ],
        'speak': _speak,
        'language': _language,
      });
      final payload = result['result'] as Map<String, dynamic>? ?? {};
      final assistantText =
          (payload['assistant_text'] as String?) ?? 'Aucune réponse';
      final audioUrl = payload['audio_url'] as String?;
      _addMessage(
        ChatMessage(role: 'assistant', text: assistantText, audioUrl: audioUrl),
      );
      if (audioUrl != null && audioUrl.isNotEmpty)
        await _playServerAudio(audioUrl);
    } catch (e) {
      if (!_offlineDemo) {
        setState(() => _offlineDemo = true);
        _addMessage(
          ChatMessage(
            role: 'system',
            text: 'Backend indisponible. Mode hors ligne activé.',
          ),
        );
        _addMessage(
          ChatMessage(
            role: 'assistant',
            text: 'Mode hors ligne — reçu : "$text"',
          ),
        );
      } else {
        _addMessage(
          ChatMessage(
            role: 'assistant',
            text: 'Mode hors ligne — reçu : "$text"',
          ),
        );
      }
    } finally {
      if (mounted)
        setState(() {
          _loading = false;
          _activeAgent = null;
        });
    }
  }

  Future<void> _toggleRecording() async {
    if (_loading || !_recorderReady) return;

    if (_isRecording) {
      final path = await _recorder.stop();
      setState(() => _isRecording = false);
      if (path == null || path.isEmpty) return;
      _recordFile = path;
      await _sendVoice(path);
      return;
    }

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      _addMessage(
        ChatMessage(role: 'system', text: 'Permission microphone refusée.'),
      );
      return;
    }

    final tempDir = await getTemporaryDirectory();
    final filePath =
        '${tempDir.path}/smartclasse_${DateTime.now().millisecondsSinceEpoch}.wav';
    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,
        numChannels: 1,
      ),
      path: filePath,
    );
    setState(() {
      _isRecording = true;
      _recordFile = filePath;
    });
  }

  Future<void> _sendVoice(String path) async {
    _addMessage(ChatMessage(role: 'user', text: '🎤 Message vocal envoyé'));
    setState(() {
      _loading = true;
      _activeAgent = 'LINGUIX Voice';
    });

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl/agents/linguix/voice_pipeline'),
      );
      request.fields['source_language_hint'] = _language;
      request.fields['target_languages'] = 'ewe,kabyie';
      request.files.add(await http.MultipartFile.fromPath('file', path));

      final streamed = await request.send().timeout(
        const Duration(seconds: 70),
      );
      final response = await http.Response.fromStream(streamed);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        final decoded = jsonDecode(response.body) as Map<String, dynamic>;
        final pipeline = decoded['pipeline'] as Map<String, dynamic>? ?? {};
        final transcription =
            pipeline['transcription'] as Map<String, dynamic>? ?? {};
        final transcriptionText = (transcription['text'] as String?) ?? '';
        String reply = 'Transcription : $transcriptionText';
        String? firstAudio;
        final translations = pipeline['translations'];
        if (translations is List && translations.isNotEmpty) {
          final first = translations.first;
          if (first is Map<String, dynamic>) {
            final txt = first['translated_instruction'] as String?;
            final audio = first['audio'];
            if (txt != null && txt.isNotEmpty) reply = txt;
            if (audio is Map<String, dynamic>)
              firstAudio = audio['audio_url'] as String?;
          }
        }
        _addMessage(
          ChatMessage(role: 'assistant', text: reply, audioUrl: firstAudio),
        );
        if (firstAudio != null && firstAudio.isNotEmpty)
          await _playServerAudio(firstAudio);
      } else {
        _addMessage(
          ChatMessage(
            role: 'system',
            text: 'Erreur API voice : ${response.statusCode}',
          ),
        );
      }
    } catch (e) {
      _addMessage(
        ChatMessage(role: 'system', text: 'Erreur upload vocal : $e'),
      );
    } finally {
      if (mounted)
        setState(() {
          _loading = false;
          _activeAgent = null;
        });
    }
  }

  Future<void> _playServerAudio(String audioUrl) async {
    final cleaned = audioUrl.startsWith('/') ? audioUrl : '/$audioUrl';
    await _player.play(UrlSource('$_baseUrl$cleaned'));
  }

  // ── Actions agents ──────────────────────────────────────────────────────

  Future<void> _runAgent(String agentId) async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _activeAgent = agentId.toUpperCase();
    });

    try {
      switch (agentId) {
        case 'diagnostix':
          await _runDiagnostix();
        case 'pilotix':
          await _runPilotix();
        case 'equitix':
          await _runEquitix();
        case 'parentix':
          await _runParentix();
        case 'orchestrator':
          await _runOrchestrator();
      }
    } finally {
      if (mounted)
        setState(() {
          _loading = false;
          _activeAgent = null;
        });
    }
  }

  Future<void> _runDiagnostix() async {
    try {
      final result = await _postJson('/agents/diagnostix/analyze', {
        'student_id': _demoStudentId,
        'student_name': _demoStudentName,
        'level': 'CM1',
        'language': _language,
      });
      final analysis = result['analysis'] as Map<String, dynamic>? ?? {};
      final teacherMessage =
          (analysis['teacher_message'] as String?) ?? 'DIAGNOSTIX prêt.';
      final nextAction = (analysis['next_action'] as String?) ?? '';
      final retro = analysis['retroactive_exercise'] as Map<String, dynamic>?;
      final buf = StringBuffer('📊 DIAGNOSTIX\n$teacherMessage');
      if (nextAction.isNotEmpty) buf.writeln('\n→ $nextAction');
      if (retro != null) {
        final title = retro['title'] as String?;
        final problem = retro['problem'] as String?;
        if (title != null) buf.writeln('\n📝 $title');
        if (problem != null) buf.writeln(problem);
      }
      _addMessage(ChatMessage(role: 'assistant', text: buf.toString().trim()));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur DIAGNOSTIX : $e'));
    }
  }

  Future<void> _runPilotix() async {
    try {
      final result = await _postJson('/agents/pilotix/dashboard', {
        'teacher_name': _demoTeacherName,
        'class_name': _demoClassName,
        'student_ids': [_demoStudentId],
        'language': _language,
      });
      final dashboard = result['dashboard'] as Map<String, dynamic>? ?? {};
      final overview =
          dashboard['class_overview'] as Map<String, dynamic>? ?? {};
      final suggestion =
          dashboard['lesson_suggestion'] as Map<String, dynamic>? ?? {};
      final classMessage =
          (suggestion['class_message'] as String?) ?? 'PILOTIX prêt.';
      final voicePrompt = (suggestion['teacher_voice_prompt'] as String?) ?? '';
      final audioUrl =
          (suggestion['audio'] as Map<String, dynamic>?)?['audio_url']
              as String?;
      _addMessage(
        ChatMessage(
          role: 'assistant',
          text:
              '🏫 PILOTIX — $_demoClassName\n$classMessage\n'
              '✅ Prêts : ${overview['ready_count'] ?? 0} | '
              '🆘 Soutien : ${overview['support_count'] ?? 0}\n'
              '👨‍🏫 $voicePrompt',
          audioUrl: audioUrl,
        ),
      );
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur PILOTIX : $e'));
    }
  }

  Future<void> _runEquitix() async {
    try {
      final result = await _postJson('/agents/equitix/risk_assessment', {
        'student_id': _demoStudentId,
        'student_name': _demoStudentName,
        'language': _language,
        'signals': {
          'attendance_days_missed': 4,
          'participation_score': 30,
          'missing_assignments': 3,
        },
      });
      final assessment = result['assessment'] as Map<String, dynamic>? ?? {};
      final riskLevel = (assessment['risk_level'] as String?) ?? 'unknown';
      final teacherAction = (assessment['teacher_action'] as String?) ?? '';
      final audioUrl =
          (assessment['voice_alert'] as Map<String, dynamic>?)?['audio_url']
              as String?;
      final emoji = riskLevel == 'high'
          ? '🔴'
          : riskLevel == 'moderate'
          ? '🟡'
          : '🟢';
      _addMessage(
        ChatMessage(
          role: 'assistant',
          text:
              '$emoji EQUITIX — $_demoStudentName\nRisque : $riskLevel\n📋 $teacherAction',
          audioUrl: audioUrl,
        ),
      );
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur EQUITIX : $e'));
    }
  }

  Future<void> _runParentix() async {
    try {
      final result = await _postJson('/agents/parentix/send_sms', {
        'student_id': _demoStudentId,
        'student_name': _demoStudentName,
        'phone_number': '',
        'language': _language,
        'dry_run': true,
      });
      final sms = result['sms'] as Map<String, dynamic>? ?? {};
      final weekly = sms['weekly_message'] as Map<String, dynamic>? ?? {};
      final text = (weekly['sms_text'] as String?) ?? 'SMS généré.';
      _addMessage(ChatMessage(role: 'assistant', text: '📱 PARENTIX\n$text'));
    } catch (e) {
      _addMessage(ChatMessage(role: 'system', text: 'Erreur PARENTIX : $e'));
    }
  }

  Future<void> _runOrchestrator() async {
    try {
      final exerciseResp = await OrchestratorApi.generateExercise(
        _baseUrl,
        studentId: _demoStudentId,
        studentName: _demoStudentName,
        level: 'CE1',
        subject: 'math',
        topic: 'fractions',
        language: _language,
      );
      final exercise = exerciseResp['exercise'] as Map<String, dynamic>?;
      if (exercise != null) {
        final title = (exercise['title'] as String?) ?? 'Exercice';
        final problem = (exercise['problem'] as String?) ?? '';
        _addMessage(
          ChatMessage(
            role: 'assistant',
            text: '✨ ORCHESTRATOR\n📝 $title\n$problem',
          ),
        );
      } else {
        _addMessage(
          ChatMessage(role: 'assistant', text: 'ORCHESTRATOR : réponse vide.'),
        );
      }
    } catch (e) {
      _addMessage(
        ChatMessage(role: 'system', text: 'Erreur ORCHESTRATOR : $e'),
      );
    }
  }

  // ── UI ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _surface,
      appBar: _buildAppBar(),
      drawer: _buildDrawer(),
      body: SafeArea(
        child: Column(
          children: [
            _buildAgentBar(),
            Expanded(child: _buildMessageList()),
            if (_loading) _buildLoadingBar(),
            _buildInputBar(),
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
          Text(
            'SmartClasse AI',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
          ),
          Text(
            'Togo · Éducation adaptative',
            style: TextStyle(fontSize: 11, color: Colors.white70),
          ),
        ],
      ),
      actions: [
        Container(
          margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: _offlineDemo
                ? Colors.orange.shade700
                : const Color(0xFF00C853),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _offlineDemo ? 'HORS LIGNE' : 'EN LIGNE',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(color: _green),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const CircleAvatar(
                  backgroundColor: _gold,
                  radius: 28,
                  child: Text(
                    'SC',
                    style: TextStyle(
                      color: _green,
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
                  style: TextStyle(
                    color: Colors.white.withAlpha(180),
                    fontSize: 12,
                  ),
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
          ..._languages.map(
            (lang) => RadioListTile<String>(
              title: Text(lang.$2),
              value: lang.$1,
              groupValue: _language,
              activeColor: _green,
              onChanged: (v) {
                setState(() => _language = v!);
                Navigator.pop(context);
              },
            ),
          ),
          const Divider(),
          SwitchListTile(
            title: const Text('Réponse audio (TTS)'),
            subtitle: const Text('Synthèse vocale des réponses'),
            secondary: const Icon(Icons.volume_up_outlined, color: _green),
            value: _speak,
            activeColor: _green,
            onChanged: (v) => setState(() => _speak = v),
          ),
          SwitchListTile(
            title: const Text('Mode hors ligne'),
            subtitle: const Text('Réponses locales sans backend'),
            secondary: const Icon(Icons.wifi_off_outlined, color: _green),
            value: _offlineDemo,
            activeColor: _green,
            onChanged: (v) => setState(() => _offlineDemo = v),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.delete_outline, color: Colors.red),
            title: const Text('Effacer la conversation'),
            onTap: () {
              setState(() => _messages.clear());
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAgentBar() {
    return Container(
      height: 56,
      color: Colors.white,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: _agents.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, i) {
          final agent = _agents[i];
          final isActive =
              _activeAgent == agent.id.toUpperCase() ||
              _activeAgent == agent.label;
          return FilledButton.tonalIcon(
            style: FilledButton.styleFrom(
              backgroundColor: isActive
                  ? agent.color
                  : agent.color.withAlpha(24),
              foregroundColor: isActive ? Colors.white : agent.color,
              padding: const EdgeInsets.symmetric(horizontal: 14),
              visualDensity: VisualDensity.compact,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
            onPressed: _loading ? null : () => _runAgent(agent.id),
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

  Widget _buildMessageList() {
    if (_messages.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: const BoxDecoration(
                color: _greenLight,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.school_outlined, size: 40, color: _green),
            ),
            const SizedBox(height: 16),
            const Text(
              'Bienvenue sur SmartClasse',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: _green,
              ),
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
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemCount: _messages.length,
      itemBuilder: (context, index) => _buildMessageTile(_messages[index]),
    );
  }

  Widget _buildMessageTile(ChatMessage message) {
    final isUser = message.role == 'user';
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
        mainAxisAlignment: isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: _greenLight,
              child: const Text(
                'AI',
                style: TextStyle(
                  fontSize: 10,
                  color: _green,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: isUser ? _green : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft: Radius.circular(isUser ? 18 : 4),
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
                      foregroundColor: _green,
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                    ),
                    onPressed: () => _playServerAudio(message.audioUrl!),
                    icon: const Icon(Icons.play_circle_outline, size: 18),
                    label: const Text(
                      'Écouter',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.only(top: 2, left: 4, right: 4),
                  child: Text(
                    '${message.timestamp.hour.toString().padLeft(2, '0')}:${message.timestamp.minute.toString().padLeft(2, '0')}',
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
              backgroundColor: _goldLight,
              child: const Icon(Icons.person_outline, size: 16, color: _green),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLoadingBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: _greenLight,
      child: Row(
        children: [
          const SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(_green),
            ),
          ),
          const SizedBox(width: 10),
          Text(
            _activeAgent != null
                ? '$_activeAgent en cours...'
                : 'Chargement...',
            style: const TextStyle(
              fontSize: 13,
              color: _green,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputBar() {
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
            child: TextField(
              controller: _inputController,
              minLines: 1,
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'Écrire en $_language...',
                hintStyle: TextStyle(color: Colors.grey.shade400),
                isDense: true,
              ),
              onSubmitted: (_) => _sendText(),
            ),
          ),
          const SizedBox(width: 8),
          Material(
            color: _green,
            borderRadius: BorderRadius.circular(24),
            child: InkWell(
              borderRadius: BorderRadius.circular(24),
              onTap: _loading ? null : _sendText,
              child: const Padding(
                padding: EdgeInsets.all(12),
                child: Icon(Icons.send_rounded, color: Colors.white, size: 20),
              ),
            ),
          ),
          if (!kIsWeb) ...[
            const SizedBox(width: 8),
            AnimatedBuilder(
              animation: _micPulseController,
              builder: (context, child) {
                return Material(
                  color: _isRecording
                      ? Color.lerp(
                          Colors.red.shade600,
                          Colors.red.shade400,
                          _micPulseController.value,
                        )!
                      : _greenLight,
                  borderRadius: BorderRadius.circular(24),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(24),
                    onTap: _loading ? null : _toggleRecording,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Icon(
                        _isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                        color: _isRecording ? Colors.white : _green,
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
