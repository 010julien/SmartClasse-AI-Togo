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
  bool    _speak       = !kIsWeb;   // TTS actif par défaut sur natif, désactivé sur web
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
    if (history.length > 10) return history.sublist(history.length - 10);
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
        final decoded           = jsonDecode(response.body) as Map<String, dynamic>;
        final pipeline          = decoded['pipeline'] as Map<String, dynamic>? ?? {};
        final transcription     = pipeline['transcription'] as Map<String, dynamic>? ?? {};
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
        case 'diagnostix':   await _runDiagnostix();
        case 'pilotix':      await _runPilotix();
        case 'equitix':      await _runEquitix();
        case 'parentix':     await _runParentix();
        case 'orchestrator': await _runOrchestrator();
      }
    } finally {
      if (mounted) setState(() { _loading = false; _activeAgent = null; });
    }
  }

  Future<void> _runDiagnostix() async {
    try {
      final result        = await _postJson('/agents/diagnostix/analyze', {
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
      final result      = await _postJson('/agents/equitix/risk_assessment', {
        'student_id':   _demoStudentId,
        'student_name': _demoStudentName,
        'language':     _language,
        'signals': {
          'attendance_days_missed': 4,
          'participation_score':    30,
          'missing_assignments':    3,
        },
      });
      final assessment    = result['assessment'] as Map<String, dynamic>? ?? {};
      final riskLevel     = (assessment['risk_level'] as String?) ?? 'unknown';
      final teacherAction = (assessment['teacher_action'] as String?) ?? '';
      final audioUrl      = (assessment['voice_alert'] as Map<String, dynamic>?)?['audio_url'] as String?;
      final emoji         = riskLevel == 'high' ? '🔴' : riskLevel == 'moderate' ? '🟡' : '🟢';
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
        language:             _language,
        languages:            _languages,
        speak:                _speak,
        offlineDemo:          _offlineDemo,
        onLanguageChanged:    (v) => setState(() => _language    = v),
        onSpeakChanged:       (v) => setState(() => _speak       = v),
        onOfflineDemoChanged: (v) => setState(() => _offlineDemo = v),
        onClearConversation:  ()  => setState(() => _messages.clear()),
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
              controller:         _inputController,
              loading:            _loading,
              isRecording:        _isRecording,
              language:           _language,
              micPulseController: _micPulseController,
              onSend:             _sendText,
              onToggleRecording:  _toggleRecording,
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
