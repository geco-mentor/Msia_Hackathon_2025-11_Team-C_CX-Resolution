// import 'package:flutter/material.dart';
// import '../models/chat_message.dart';
// import '../services/chat_service.dart';

// class ChatViewModel extends ChangeNotifier {
//   final ChatService _chatService = ChatService();

//   List<ChatMessage> messages = [];
//   bool isLoading = false;

//   Future<void> sendMessage(String msg) async {
//     messages.add(ChatMessage(message: msg, isUser: true));
//     notifyListeners();

//     isLoading = true;
//     notifyListeners();

//     try {
//       String response = await _chatService.sendMessage(msg);

//       messages.add(ChatMessage(message: response, isUser: false));
//     } catch (e) {
//       messages.add(ChatMessage(message: "Error: $e", isUser: false));
//     }

//     isLoading = false;
//     notifyListeners();
//   }
// }


import 'package:flutter/material.dart';

import '../models/chat_message.dart';
import '../services/chat_service.dart';

class ChatViewModel extends ChangeNotifier {
  final ChatService _chatService = ChatService();

  List<ChatMessage> messages = [];
  bool isLoading = false;
  String phoneNumber = "+60132211009";

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

  Future<void> sendMessage(String msg) async {
    messages.add(ChatMessage(message: msg, isUser: true));
    notifyListeners();

    isLoading = true;
    notifyListeners();

    try {
      String response =
          await _chatService.sendMessage(msg, phoneNumber: phoneNumber);

      // AUTO SHOW PLANS (not from API)
      messages.add(
        ChatMessage(
          message: response,
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
