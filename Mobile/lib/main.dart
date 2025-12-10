import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart';

import 'viewmodels/chat_viewmodel.dart';
import 'views/chat_screen.dart';
import 'views/dashboard_screen.dart';
import 'views/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load .env file
    await dotenv.load(
    fileName: kIsWeb ? "assets/env/.env" : ".env",
  );


  runApp(
    ChangeNotifierProvider(
      create: (_) => ChatViewModel(),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const SplashScreen(),
      routes: {
        '/dashboard': (_) => const DashboardScreen(),
        '/chat': (_) => ChatScreen(),
      },
    );
  }
}
