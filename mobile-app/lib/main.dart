import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'services/config_service.dart';
import 'screens/home_screen.dart';
import 'screens/config_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化配置服务
  final configService = ConfigService();
  await configService.init();

  runApp(MyApp(configService: configService));
}

class MyApp extends StatelessWidget {
  final ConfigService configService;

  const MyApp({Key? key, required this.configService}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ConfigService>.value(value: configService),
        Provider<ApiService>(
          create: (_) => ApiService(baseUrl: configService.serverUrl),
        ),
      ],
      child: MaterialApp(
        title: '安全整改管理',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: configService.serverUrl.isEmpty
            ? const ConfigScreen()
            : const HomeScreen(),
        routes: {
          '/home': (context) => const HomeScreen(),
          '/config': (context) => const ConfigScreen(),
        },
      ),
    );
  }
}