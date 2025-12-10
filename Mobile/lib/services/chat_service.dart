// import 'dart:convert';

// import 'package:http/http.dart' as http;

// class ChatService {
//   final String baseUrl =
//       "https://bteng7ing0.execute-api.ap-southeast-1.amazonaws.com/prod/chat";

//   Future<String> sendMessage(
//     String userMessage, {
//     required String phoneNumber,
//   }) async {
//     final response = await http.post(
//       Uri.parse(baseUrl),
//       headers: {"Content-Type": "application/json"},
//       body: jsonEncode({
//         "message": userMessage,
//         "phone_number": phoneNumber,
//         "channel": "mobile",  // Mobile app - skip PIN verification
//       }),
//     );

//     if (response.statusCode == 200) {
//       final data = jsonDecode(response.body);
//       // Try different possible response field names
//       final responseText = data["response"] ?? 
//                           data["message"] ?? 
//                           data["reply"] ?? 
//                           data["answer"] ??
//                           data["body"] ??
//                           response.body;
      
//       if (responseText == null) {
//         throw Exception("API response does not contain expected fields. Response: ${response.body}");
//       }
      
//       return responseText.toString();
//     } else {
//       throw Exception("Failed to load response: ${response.statusCode} - ${response.body}");
//     }
//   }
// }

import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

class ChatService {
  // Read the value from .env
  final String baseUrl = dotenv.env['APIKEY'] ?? "";

  Future<String> sendMessage(
    String userMessage, {
    required String phoneNumber,
  }) async {
    if (baseUrl.isEmpty) {
      throw Exception("APIKEY is missing from .env file");
    }

    final response = await http.post(
      Uri.parse(baseUrl),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "message": userMessage,
        "phone_number": phoneNumber,
        "channel": "mobile",
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final responseText = data["response"] ??
          data["message"] ??
          data["reply"] ??
          data["answer"] ??
          data["body"] ??
          response.body;

      if (responseText == null) {
        throw Exception(
            "API response missing fields. Response: ${response.body}");
      }

      return responseText.toString();
    } else {
      throw Exception(
          "Failed: ${response.statusCode} - ${response.body}");
    }
  }
}


