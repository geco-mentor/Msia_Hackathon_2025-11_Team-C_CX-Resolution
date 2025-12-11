import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

/// Response from chat API including session tracking
class ChatResponse {
  final String message;
  final String? sessionId;
  final bool requiresFollowup;

  ChatResponse({
    required this.message,
    this.sessionId,
    this.requiresFollowup = false,
  });
}

class ChatService {
  // Read the value from .env
  final String baseUrl = dotenv.env['APIKEY'] ?? "";

  /// Detect channel based on platform
  /// - Web (Chrome): requires PIN verification
  /// - Mobile (iOS/Android): skip PIN (user authenticated via app)
  String get _channel => kIsWeb ? "web" : "mobile";

  Future<ChatResponse> sendMessage(
    String userMessage, {
    required String phoneNumber,
    String? sessionId,  // Pass session_id to continue conversation
  }) async {
    if (baseUrl.isEmpty) {
      throw Exception("APIKEY is missing from .env file");
    }

    final body = {
      "message": userMessage,
      "phone_number": phoneNumber,
      "channel": _channel,  // Auto-detect: web requires PIN, mobile skips
    };
    
    // Include session_id if continuing a conversation
    if (sessionId != null) {
      body["session_id"] = sessionId;
    }

    final response = await http.post(
      Uri.parse(baseUrl),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      
      // Extract response text
      final responseText = data["message"] ?? 
                          data["response"] ?? 
                          data["reply"] ?? 
                          data["answer"] ??
                          data["body"] ??
                          response.body;
      
      if (responseText == null) {
        throw Exception(
            "API response missing fields. Response: ${response.body}");
      }
      
      return ChatResponse(
        message: responseText.toString(),
        sessionId: data["session_id"],
        requiresFollowup: data["requires_followup"] ?? false,
      );
    } else {
      throw Exception(
          "Failed: ${response.statusCode} - ${response.body}");
    }
  }
}
