
import 'package:test/test.dart';
import 'package:medstory/models/timeline_item.dart';

void main() {
  group('TimelineItem', () {
    test('fromJson creates correct object', () {
      final json = {
        'id': 1,
        'type': 'status',
        'text': 'Hello World',
        'image_url': null,
        'created_at': '2023-10-27T10:00:00.000Z'
      };

      final item = TimelineItem.fromJson(json);

      expect(item.id, 1);
      expect(item.type, 'status');
      expect(item.text, 'Hello World');
      expect(item.imageUrl, null);
      expect(item.createdAt.year, 2023);
    });
  });
}
