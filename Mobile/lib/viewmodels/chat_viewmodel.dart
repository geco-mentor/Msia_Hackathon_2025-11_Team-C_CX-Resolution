import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../models/chat_message.dart';
import '../services/chat_service.dart';

class ChatViewModel extends ChangeNotifier {
  final ChatService _chatService = ChatService();

  List<ChatMessage> messages = [];
  bool isLoading = false;
  String phoneNumber = dotenv.env['PHONE_NUMBER'] ?? "";
  
  /// Session ID for maintaining conversation state across messages
  /// Critical for multi-turn flows like PIN verification
  String? _sessionId;

  // STATIC PLANS (since not coming from API)
  List<Map<String, String>> prepaidPlans = [
    {
      "title": "CelcomDigi Prepaid RM25",
      "subtitle": "High-Speed Data",
      "details": "8GB High Speed\nUnlimited Social Apps\nFree 5G Access",
    },
    {
      "title": "CelcomDigi Prepaid RM35",
      "subtitle": "More Data & Calls",
      "details": "15GB High Speed\nUnlimited Calls\nFree 5G Access",
    },
    {
      "title": "CelcomDigi Prepaid RM45",
      "subtitle": "More Value",
      "details": "20GB High Speed\nUnlimited Apps\nFree 5G Access",
    },
  ];

  /// Clear session to start a new conversation
  void clearSession() {
    _sessionId = null;
    messages.clear();
    notifyListeners();
  }

  Future<void> sendMessage(String msg) async {
    messages.add(ChatMessage(message: msg, isUser: true));
    notifyListeners();

    isLoading = true;
    notifyListeners();

    try {
      // Pass session_id to continue the conversation
      ChatResponse response = await _chatService.sendMessage(
        msg,
        phoneNumber: phoneNumber,
        sessionId: _sessionId,
      );

      // Store session_id for follow-up messages (PIN verification, etc.)
      if (response.sessionId != null) {
        _sessionId = response.sessionId;
      }

      // AUTO SHOW PLANS (not from API)
      messages.add(
        ChatMessage(
          message: response.message,
          isUser: false,
          cards: prepaidPlans,
        ),
      );
    } catch (e) {
      messages.add(ChatMessage(message: "Error: $e", isUser: false));
    }

    isLoading = false;
    notifyListeners();
  }
}
