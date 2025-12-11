
import 'package:flutter/foundation.dart';
import '../models/timeline_item.dart';
import '../services/api_client.dart';

class TimelineProvider extends ChangeNotifier {
  final ApiClient apiClient;
  List<TimelineItem> _items = [];
  bool _isLoading = false;
  String? _error;

  TimelineProvider({required this.apiClient});

  List<TimelineItem> get items => _items;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchTimeline() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final List<dynamic> data = await apiClient.get('/api/timeline/');
      _items = data.map((item) => TimelineItem.fromJson(item)).toList();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addStatusUpdate(String text) async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await apiClient.post('/api/timeline/', {
        'type': 'status',
        'text': text,
      });
      _items.insert(0, TimelineItem.fromJson(data));
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> addImage(String text, List<int> fileBytes, String filename) async {
     _isLoading = true;
    notifyListeners();

    try {
      final data = await apiClient.postMultipart(
        '/api/timeline/', 
        {'type': 'image', 'text': text},
        fileBytes,
        filename
      );
      _items.insert(0, TimelineItem.fromJson(data));
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
