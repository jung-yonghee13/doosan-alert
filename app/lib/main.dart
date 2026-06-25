import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

// Android 는 google-services.json + google-services Gradle 플러그인으로
// 초기화하므로 firebase_options.dart 가 필요 없습니다.

const String kFcmTopic = 'doosan_games';
const String kTeamCode = 'OB'; // 두산
const String kTeamName = '두산';

final FlutterLocalNotificationsPlugin _localNotifications =
    FlutterLocalNotificationsPlugin();

const AndroidNotificationChannel _channel = AndroidNotificationChannel(
  'doosan_games_channel',
  '두산 경기 알림',
  description: '새 경기 일정이 등록되면 알려드립니다.',
  importance: Importance.high,
);

/// 백그라운드(앱 종료/백그라운드 상태)에서 메시지를 받는 핸들러.
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // 백그라운드에서는 OS가 notification 페이로드를 자동 표시하므로 별도 처리 불필요.
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);

  await _setupLocalNotifications();
  await _setupFcm();

  runApp(const DoosanAlertApp());
}

Future<void> _setupLocalNotifications() async {
  const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
  const iosInit = DarwinInitializationSettings();
  await _localNotifications.initialize(
    const InitializationSettings(android: androidInit, iOS: iosInit),
  );
  await _localNotifications
      .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>()
      ?.createNotificationChannel(_channel);
}

Future<void> _setupFcm() async {
  final messaging = FirebaseMessaging.instance;

  // 알림 권한 요청 (iOS / Android 13+)
  await messaging.requestPermission(alert: true, badge: true, sound: true);

  // 토픽 구독: 백엔드가 이 토픽으로 푸시를 보냅니다.
  await messaging.subscribeToTopic(kFcmTopic);

  // 포그라운드(앱이 열려 있을 때) 메시지는 직접 로컬 알림으로 표시.
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    final notification = message.notification;
    if (notification != null) {
      _localNotifications.show(
        notification.hashCode,
        notification.title,
        notification.body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            _channel.id,
            _channel.name,
            channelDescription: _channel.description,
            importance: Importance.high,
            priority: Priority.high,
          ),
          iOS: const DarwinNotificationDetails(),
        ),
      );
    }
  });
}

class DoosanAlertApp extends StatelessWidget {
  const DoosanAlertApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '$kTeamName 경기 알림',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF131230), // 두산 네이비
        useMaterial3: true,
      ),
      home: const ScheduleScreen(),
    );
  }
}

class Game {
  final String id;
  final String date;
  final String dateTime;
  final String stadium;
  final String homeName;
  final String awayName;
  final String status;

  Game.fromJson(Map<String, dynamic> j)
      : id = j['gameId'] ?? '',
        date = j['gameDate'] ?? '',
        dateTime = j['gameDateTime'] ?? '',
        stadium = j['stadium'] ?? '',
        homeName = j['homeTeamName'] ?? '',
        awayName = j['awayTeamName'] ?? '',
        status = j['statusCode'] ?? '';
}

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  late Future<List<Game>> _future;

  @override
  void initState() {
    super.initState();
    _future = _fetchGames();
  }

  Future<List<Game>> _fetchGames() async {
    final now = DateTime.now();
    final from = DateFormat('yyyy-MM-dd').format(now);
    final to =
        DateFormat('yyyy-MM-dd').format(now.add(const Duration(days: 120)));
    final uri = Uri.parse(
      'https://api-gw.sports.naver.com/schedule/games'
      '?fields=basic,schedule&upperCategoryId=kbaseball&categoryId=kbo'
      '&fromDate=$from&toDate=$to&size=500',
    );
    final resp = await http.get(uri, headers: {'User-Agent': 'Mozilla/5.0'});
    final body = json.decode(resp.body);
    final games = (body['result']?['games'] as List? ?? [])
        .map((g) => Game.fromJson(g))
        .where((g) =>
            g.homeName == kTeamName || g.awayName == kTeamName)
        .toList();
    return games;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('$kTeamName 경기 일정')),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() => _future = _fetchGames());
          await _future;
        },
        child: FutureBuilder<List<Game>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return ListView(children: [
                const SizedBox(height: 200),
                Center(child: Text('불러오기 실패: ${snap.error}')),
              ]);
            }
            final games = snap.data ?? [];
            if (games.isEmpty) {
              return const Center(child: Text('예정된 경기가 없습니다.'));
            }
            return ListView.separated(
              itemCount: games.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, i) {
                final g = games[i];
                final isHome = g.homeName == kTeamName;
                final opponent = isHome ? g.awayName : g.homeName;
                return ListTile(
                  leading: CircleAvatar(
                    child: Text(isHome ? '홈' : '원'),
                  ),
                  title: Text('vs $opponent'),
                  subtitle: Text('${g.date} · ${g.stadium}'),
                  trailing: Text(_statusLabel(g.status)),
                );
              },
            );
          },
        ),
      ),
    );
  }

  String _statusLabel(String code) {
    switch (code) {
      case 'BEFORE':
        return '예정';
      case 'STARTED':
        return '진행중';
      case 'RESULT':
        return '종료';
      case 'CANCEL':
        return '취소';
      default:
        return '';
    }
  }
}
