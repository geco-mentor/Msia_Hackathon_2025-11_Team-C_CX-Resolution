import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../services/chat_service.dart';

class ChatViewModel extends ChangeNotifier {
  final ChatService _chatService = ChatService();

  List<ChatMessage> messages = [];
  bool isLoading = false;

  Future<void> sendMessage(String msg) async {
    messages.add(ChatMessage(message: msg, isUser: true));
    notifyListeners();

    isLoading = true;
    notifyListeners();

    try {
      String response = await _chatService.sendMessage(msg);

      messages.add(ChatMessage(message: response, isUser: false));
    } catch (e) {
      messages.add(ChatMessage(message: "Error: $e", isUser: false));
    }

    isLoading = false;
    notifyListeners();
  }
}
