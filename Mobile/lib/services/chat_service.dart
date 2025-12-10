// import 'dart:convert';
// import 'package:http/http.dart' as http;

// class ChatService {
//   final String baseUrl = "https://qo8koiiv17.execute-api.eu-central-1.amazonaws.com/prod1/chat";

//   Future<String> sendMessage(String userMessage) async {
//     final response = await http.post(
//       Uri.parse(baseUrl),
//       headers: {"Content-Type": "application/json"},
//       body: jsonEncode({"message": userMessage}),
//     );

//     if (response.statusCode == 200) {
//       final data = jsonDecode(response.body);
//       return data["response"]; // <-- Adjust based on API response format
//     } else {
//       throw Exception("Failed to load response");
//     }
//   }
// }

import 'dart:convert';

import 'package:http/http.dart' as http;

class ChatService {
  final String baseUrl =
      "https://bteng7ing0.execute-api.ap-southeast-1.amazonaws.com/prod/chat";

  Future<String> sendMessage(
    String userMessage, {
    required String phoneNumber,
  }) async {
    final response = await http.post(
      Uri.parse(baseUrl),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "message": userMessage,
        "phone_number": phoneNumber,
        "channel": "mobile",  // Mobile app - skip PIN verification
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Try different possible response field names
      final responseText = data["response"] ?? 
                          data["message"] ?? 
                          data["reply"] ?? 
                          data["answer"] ??
                          data["body"] ??
                          response.body;
      
      if (responseText == null) {
        throw Exception("API response does not contain expected fields. Response: ${response.body}");
      }
      
      return responseText.toString();
    } else {
      throw Exception("Failed to load response: ${response.statusCode} - ${response.body}");
    }
  }
}

