
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/timeline_provider.dart';
import '../services/api_client.dart';
import 'screens/timeline_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // In a real app, baseUrl would come from env config
    const apiUrl = String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8000');
    final apiClient = ApiClient(baseUrl: apiUrl);

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => TimelineProvider(apiClient: apiClient)),
      ],
      child: MaterialApp(
        title: 'MedStory',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const TimelineScreen(),
      ),
    );
  }
}
