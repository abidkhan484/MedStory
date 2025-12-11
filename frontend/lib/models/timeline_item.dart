
class TimelineItem {
  final int? id;
  final String type;
  final String? text;
  final String? imageUrl;
  final DateTime createdAt;

  TimelineItem({
    this.id,
    required this.type,
    this.text,
    this.imageUrl,
    required this.createdAt,
  });

  factory TimelineItem.fromJson(Map<String, dynamic> json) {
    return TimelineItem(
      id: json['id'],
      type: json['type'],
      text: json['text'],
      imageUrl: json['image_url'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'text': text,
      'image_url': imageUrl,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
