
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/timeline_provider.dart';
import '../services/api_client.dart';
import '../models/timeline_item.dart';
import 'post_update_screen.dart';

class TimelineScreen extends StatefulWidget {
  const TimelineScreen({super.key});

  @override
  State<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends State<TimelineScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TimelineProvider>().fetchTimeline();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MedStory Timeline'),
      ),
      body: Consumer<TimelineProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.items.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.error != null) {
            return Center(child: Text('Error: ${provider.error}'));
          }

          return ListView.builder(
            itemCount: provider.items.length,
            itemBuilder: (context, index) {
              final item = provider.items[index];
              return TimelineItemWidget(
                item: item, 
                baseUrl: provider.apiClient.baseUrl
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const PostUpdateScreen()),
          );
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}

class TimelineItemWidget extends StatelessWidget {
  final TimelineItem item;
  final String baseUrl;

  const TimelineItemWidget({super.key, required this.item, required this.baseUrl});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              item.createdAt.toString(),
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            if (item.text != null) ...[
              Text(item.text!),
              const SizedBox(height: 8),
            ],
            if (item.imageUrl != null)
              Image.network(
                _getImageUrl(item.imageUrl!),
                errorBuilder: (context, error, stackTrace) => 
                    const Text('Could not load image'),
              ),
          ],
        ),
      ),
    );
  }

  String _getImageUrl(String url) {
    if (url.startsWith('http')) {
      return url;
    }
    // Remove trailing slash from base if present and leading from url if present
    final cleanBase = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
    final cleanUrl = url.startsWith('/') ? url : '/$url';
    return '$cleanBase$cleanUrl';
  }
}
