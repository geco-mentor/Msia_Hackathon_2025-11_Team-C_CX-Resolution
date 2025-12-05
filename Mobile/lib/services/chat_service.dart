import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatService {
  final String baseUrl = "https://qo8koiiv17.execute-api.eu-central-1.amazonaws.com/prod1/chat";

  Future<String> sendMessage(String userMessage) async {
    final response = await http.post(
      Uri.parse(baseUrl),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"message": userMessage}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data["response"]; // <-- Adjust based on API response format
    } else {
      throw Exception("Failed to load response");
    }
  }
}
