import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/chat_viewmodel.dart';

class ChatScreen extends StatelessWidget {
  ChatScreen({super.key});

  final TextEditingController _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        //leading: Icon(Icons.arrow_back, color: Colors.black),
        title: Row(
                children: [
                  Image.asset(
                    "assets/logo.png",
                    height: 26,
                    width: 26,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    "AI-RA by CelcomDigi",
                    style: TextStyle(color: Colors.black),
                  ),
                ],
              ),

        // actions: const [
        //   Padding(
        //     padding: EdgeInsets.only(right: 12),
        //     child: Icon(Icons.close, color: Colors.black),
        //   )
        // ],
      ),
      body: Consumer<ChatViewModel>(
        builder: (context, vm, child) {
          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: vm.messages.length,
                  itemBuilder: (context, index) {
                    final msg = vm.messages[index];
                    final isUser = msg.isUser;

                    return Column(
                      crossAxisAlignment: isUser
                          ? CrossAxisAlignment.end
                          : CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(14),
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          constraints: const BoxConstraints(maxWidth: 300),
                          decoration: BoxDecoration(
                            color: isUser
                                ? const Color(0xFF2A1856) // purple bubble
                                : const Color(0xFFF3F3F3), // light bot bubble
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Text(
                            msg.message,
                            style: TextStyle(
                              color: isUser ? Colors.white : Colors.black87,
                              fontSize: 15,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          "a few seconds ago",
                          style: TextStyle(fontSize: 11, color: Colors.grey),
                        ),
                        const SizedBox(height: 10),
                      ],
                    );
                  },
                ),
              ),

              if (vm.isLoading)
                const Padding(
                  padding: EdgeInsets.all(8),
                  child: CircularProgressIndicator(),
                ),

              // Suggested Quick Reply Buttons
              if (vm.messages.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    children: [
                      _quickButton("Login and Registration", vm),
                      _quickButton(
                          "Account Verification and View All Numbers", vm),
                      _quickButton("View or Download Statement", vm),
                      _quickButton("Guide to CelcomDigi App", vm),
                    ],
                  ),
                ),

              // Input Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                        color: Colors.black12,
                        blurRadius: 4,
                        offset: Offset(0, -2))
                  ],
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(color: Colors.blue, width: 1),
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: TextField(
                          controller: _controller,
                          decoration: const InputDecoration(
                            border: InputBorder.none,
                            hintText: "Write a reply...",
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    CircleAvatar(
                      backgroundColor: Colors.blue,
                      child: IconButton(
                        icon: const Icon(Icons.send, color: Colors.white),
                        onPressed: () {
                          if (_controller.text.trim().isNotEmpty) {
                            final text = _controller.text.trim();
                            _controller.clear();
                            vm.sendMessage(text);
                          }
                        },
                      ),
                    )
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _quickButton(String text, ChatViewModel vm) {
    return GestureDetector(
      onTap: () => vm.sendMessage(text),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
        decoration: BoxDecoration(
          color: const Color(0xFFDFDFF7),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          text,
          style: const TextStyle(color: Colors.black87),
        ),
      ),
    );
  }
}
