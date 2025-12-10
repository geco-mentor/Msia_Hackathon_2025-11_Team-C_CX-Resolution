// class ChatMessage {
//   final String message;
//   final bool isUser;

//   ChatMessage({required this.message, required this.isUser});
// }
// // a

class ChatMessage {
  final String message;
  final bool isUser;
  final List<Map<String, String>>? cards;

  ChatMessage({
    required this.message,
    required this.isUser,
    this.cards,
  });
}
