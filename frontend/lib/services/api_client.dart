
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiClient {
  final String baseUrl;
  final http.Client client;

  ApiClient({required this.baseUrl, http.Client? client})
      : client = client ?? http.Client();

  Future<dynamic> get(String endpoint) async {
    final response = await client.get(Uri.parse('$baseUrl$endpoint'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load data: ${response.statusCode}');
    }
  }

  Future<dynamic> post(String endpoint, Map<String, String> body) async {
    final response = await client.post(
      Uri.parse('$baseUrl$endpoint'),
      body: body,
    );
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to post data: ${response.statusCode}');
    }
  }

  Future<dynamic> postMultipart(String endpoint, Map<String, String> fields,
      List<int> fileBytes, String filename) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl$endpoint'));

    fields.forEach((k, v) {
      request.fields[k] = v;
    });

    if (fileBytes.isNotEmpty) {
      MediaType? contentType;
      final ext = filename.split('.').last.toLowerCase();
      if (['jpg', 'jpeg'].contains(ext)) {
        contentType = MediaType('image', 'jpeg');
      } else if (['png'].contains(ext)) {
        contentType = MediaType('image', 'png');
      } else if (['pdf'].contains(ext)) {
        contentType = MediaType('application', 'pdf');
      } else {
        contentType = MediaType('application', 'octet-stream');
      }

      request.files.add(http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: filename,
        contentType: contentType,
      ));
    }

    var streamedResponse = await client.send(request);
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to upload file: ${response.statusCode}');
    }
  }
}
