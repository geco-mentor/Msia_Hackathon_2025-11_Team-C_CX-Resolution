// import 'package:flutter/material.dart';
// import 'package:provider/provider.dart';

// import '../viewmodels/chat_viewmodel.dart';

// class ChatScreen extends StatelessWidget {
//   ChatScreen({super.key});

//   final TextEditingController _controller = TextEditingController();

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         backgroundColor: Colors.white,
//         elevation: 0.5,
//         //leading: Icon(Icons.arrow_back, color: Colors.black),
//         title: Row(
//                 children: [
//                   Image.asset(
//                     "assets/images/logocelcomdigi.png",
//                     height: 26,
//                     width: 26,
//                   ),
//                   const SizedBox(width: 8),
//                   const Text(
//                     "AI-RA by CelcomDigi",
//                     style: TextStyle(color: Colors.black),
//                   ),
//                 ],
//               ),

//         // actions: const [
//         //   Padding(
//         //     padding: EdgeInsets.only(right: 12),
//         //     child: Icon(Icons.close, color: Colors.black),
//         //   )
//         // ],
//       ),
//       body: Consumer<ChatViewModel>(
//         builder: (context, vm, child) {
//           return Column(
//             children: [
//               Expanded(
//                 child: ListView.builder(
//                   padding: const EdgeInsets.all(16),
//                   itemCount: vm.messages.length,
//                   itemBuilder: (context, index) {
//                     final msg = vm.messages[index];
//                     final isUser = msg.isUser;

//                     return Column(
//                       crossAxisAlignment: isUser
//                           ? CrossAxisAlignment.end
//                           : CrossAxisAlignment.start,
//                       children: [
//                         Container(
//                           padding: const EdgeInsets.all(14),
//                           margin: const EdgeInsets.symmetric(vertical: 4),
//                           constraints: const BoxConstraints(maxWidth: 300),
//                           decoration: BoxDecoration(
//                             color: isUser
//                                 ? const Color(0xFF2A1856) // purple bubble
//                                 : const Color(0xFFF3F3F3), // light bot bubble
//                             borderRadius: BorderRadius.circular(14),
//                           ),
//                           child: Text(
//                             msg.message,
//                             style: TextStyle(
//                               color: isUser ? Colors.white : Colors.black87,
//                               fontSize: 15,
//                             ),
//                           ),
//                         ),
//                         const SizedBox(height: 4),
//                         const Text(
//                           "a few seconds ago",
//                           style: TextStyle(fontSize: 11, color: Colors.grey),
//                         ),
//                         const SizedBox(height: 10),
//                       ],
//                     );
//                   },
//                 ),
//               ),

//               if (vm.isLoading)
//                 const Padding(
//                   padding: EdgeInsets.all(8),
//                   child: CircularProgressIndicator(),
//                 ),

//               // Suggested Quick Reply Buttons
//               if (vm.messages.isNotEmpty)
//                 Padding(
//                   padding: const EdgeInsets.only(bottom: 8),
//                   child: Wrap(
//                     spacing: 8,
//                     runSpacing: 6,
//                     children: [
//                       _quickButton("Login and Registration", vm),
//                       _quickButton(
//                           "Account Verification and View All Numbers", vm),
//                       _quickButton("View or Download Statement", vm),
//                       _quickButton("Guide to CelcomDigi App", vm),
//                     ],
//                   ),
//                 ),

//               // Input Bar
//               Container(
//                 padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
//                 decoration: const BoxDecoration(
//                   color: Colors.white,
//                   boxShadow: [
//                     BoxShadow(
//                         color: Colors.black12,
//                         blurRadius: 4,
//                         offset: Offset(0, -2))
//                   ],
//                 ),
//                 child: Row(
//                   children: [
//                     Expanded(
//                       child: Container(
//                         padding: const EdgeInsets.symmetric(horizontal: 16),
//                         decoration: BoxDecoration(
//                           color: Colors.white,
//                           border: Border.all(color: Colors.blue, width: 1),
//                           borderRadius: BorderRadius.circular(25),
//                         ),
//                         child: TextField(
//                           controller: _controller,
//                           decoration: const InputDecoration(
//                             border: InputBorder.none,
//                             hintText: "Write a reply...",
//                           ),
//                         ),
//                       ),
//                     ),
//                     const SizedBox(width: 8),
//                     CircleAvatar(
//                       backgroundColor: Colors.blue,
//                       child: IconButton(
//                         icon: const Icon(Icons.send, color: Colors.white),
//                         onPressed: () {
//                           if (_controller.text.trim().isNotEmpty) {
//                             final text = _controller.text.trim();
//                             _controller.clear();
//                             vm.sendMessage(text);
//                           }
//                         },
//                       ),
//                     )
//                   ],
//                 ),
//               ),
//             ],
//           );
//         },
//       ),
//     );
//   }

//   Widget _quickButton(String text, ChatViewModel vm) {
//     return GestureDetector(
//       onTap: () => vm.sendMessage(text),
//       child: Container(
//         padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
//         decoration: BoxDecoration(
//           color: const Color(0xFFDFDFF7),
//           borderRadius: BorderRadius.circular(12),
//         ),
//         child: Text(
//           text,
//           style: const TextStyle(color: Colors.black87),
//         ),
//       ),
//     );
//   }
// }


// import 'package:flutter/material.dart';
// import 'package:provider/provider.dart';

// import '../models/chat_message.dart';
// import '../viewmodels/chat_viewmodel.dart';

// class ChatScreen extends StatelessWidget {
//   ChatScreen({super.key});

//   final TextEditingController _controller = TextEditingController();

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         backgroundColor: Colors.white,
//         elevation: 0.5,
//         title: Row(
//           children: [
//             Image.asset("assets/images/logocelcomdigi.png",
//                 height: 26, width: 26),
//             const SizedBox(width: 8),
//             const Text(
//               "AI-RA by CelcomDigi",
//               style: TextStyle(color: Colors.black),
//             ),
//           ],
//         ),
//       ),

//       body: Consumer<ChatViewModel>(
//         builder: (context, vm, child) {
//           return Column(
//             children: [
//               Expanded(
//                 child: ListView.builder(
//                   padding: const EdgeInsets.all(16),
//                   itemCount: vm.messages.length,
//                   itemBuilder: (context, index) {
//                     final ChatMessage msg = vm.messages[index];

//                     return Column(
//                       crossAxisAlignment: msg.isUser
//                           ? CrossAxisAlignment.end
//                           : CrossAxisAlignment.start,
//                       children: [
//                         // Chat Bubble
//                         Container(
//                           padding: const EdgeInsets.all(14),
//                           margin: const EdgeInsets.symmetric(vertical: 6),
//                           constraints: const BoxConstraints(maxWidth: 320),
//                           decoration: BoxDecoration(
//                             color: msg.isUser
//                                 ? const Color(0xFF2A1856)
//                                 : const Color(0xFFF3F3F3),
//                             borderRadius: BorderRadius.circular(14),
//                           ),
//                           child: Text(
//                             msg.message,
//                             style: TextStyle(
//                               color: msg.isUser ? Colors.white : Colors.black87,
//                               fontSize: 15,
//                             ),
//                           ),
//                         ),

//                         const SizedBox(height: 6),

//                         // --- SHOW CARDS IF AVAILABLE ---
//                         if (msg.cards != null) _buildPlanSection(msg.cards!),

//                         const SizedBox(height: 12),
//                       ],
//                     );
//                   },
//                 ),
//               ),

//               if (vm.isLoading)
//                 const Padding(
//                   padding: EdgeInsets.all(8),
//                   child: CircularProgressIndicator(),
//                 ),

//               _buildInputBar(vm),
//             ],
//           );
//         },
//       ),
//     );
//   }

//   // ================================
//   // CARD SECTION UI
//   // ================================
//   Widget _buildPlanSection(List<Map<String, String>> cards) {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         const Text(
//           "Digi Prepaid Digi many plans available\nTap to learn more!",
//           style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
//         ),
//         const SizedBox(height: 12),

//         SizedBox(
//           height: 210,
//           child: ListView.builder(
//             scrollDirection: Axis.horizontal,
//             itemCount: cards.length,
//             itemBuilder: (context, index) {
//               final item = cards[index];

//               return Container(
//                 width: 220,
//                 margin: const EdgeInsets.only(right: 12),
//                 padding: const EdgeInsets.all(14),
//                 decoration: BoxDecoration(
//                   color: Colors.white,
//                   border: Border.all(color: Colors.black12),
//                   borderRadius: BorderRadius.circular(12),
//                   boxShadow: const [
//                     BoxShadow(
//                         color: Colors.black12, blurRadius: 3, offset: Offset(0, 1))
//                   ],
//                 ),
//                 child: Column(
//                   crossAxisAlignment: CrossAxisAlignment.start,
//                   children: [
//                     Text(item["title"]!,
//                         style: const TextStyle(
//                             fontWeight: FontWeight.bold, fontSize: 15)),
//                     const SizedBox(height: 6),
//                     Text(item["subtitle"]!,
//                         style: TextStyle(
//                             color: Colors.blue.shade700,
//                             fontWeight: FontWeight.w500)),
//                     const SizedBox(height: 10),
//                     Text(item["details"]!,
//                         style:
//                             const TextStyle(fontSize: 13, color: Colors.black87)),
//                     const Spacer(),
//                     ElevatedButton(
//                       style: ElevatedButton.styleFrom(
//                           backgroundColor: Colors.blue),
//                       onPressed: () {},
//                       child: const Text("View Details", style: TextStyle(color: Colors.white)),
//                     )
//                   ],
//                 ),
//               );
//             },
//           ),
//         ),

//         const SizedBox(height: 12),

//         Center(
//           child: ElevatedButton(
//             style: ElevatedButton.styleFrom(
//               backgroundColor: Colors.blue,
//               shape: RoundedRectangleBorder(
//                 borderRadius: BorderRadius.circular(25),
//               ),
//             ),
//             onPressed: () {},
//             child: const Text("Compare All Kuning Plans",style: TextStyle(color: Colors.white)),
//           ),
//         ),
//       ],
//     );
//   }

//   // ================================
//   // INPUT BAR
//   // ================================
//   Widget _buildInputBar(ChatViewModel vm) {
//     return Container(
//       padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
//       decoration: const BoxDecoration(color: Colors.white, boxShadow: [
//         BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, -2))
//       ]),
//       child: Row(
//         children: [
//           Expanded(
//             child: Container(
//               padding: const EdgeInsets.symmetric(horizontal: 16),
//               decoration: BoxDecoration(
//                 border: Border.all(color: Colors.blue),
//                 borderRadius: BorderRadius.circular(25),
//               ),
//               child: TextField(
//                 controller: _controller,
//                 decoration: const InputDecoration(
//                   border: InputBorder.none,
//                   hintText: "Write a reply...",
//                 ),
//               ),
//             ),
//           ),
//           const SizedBox(width: 8),
//           CircleAvatar(
//             backgroundColor: Colors.blue,
//             child: IconButton(
//               icon: const Icon(Icons.send, color: Colors.white),
//               onPressed: () {
//                 if (_controller.text.trim().isNotEmpty) {
//                   vm.sendMessage(_controller.text.trim());
//                   _controller.clear();
//                 }
//               },
//             ),
//           )
//         ],
//       ),
//     );
//   }
// }


import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/chat_message.dart';
import '../viewmodels/chat_viewmodel.dart';

class ChatScreen extends StatelessWidget {
  ChatScreen({super.key});

  final TextEditingController _controller = TextEditingController();
  static const Color _primary = Color.fromARGB(255, 5, 29, 77);
  static const Color _accent = Color(0xFF2196F3);
  static const Color _surface = Color(0xFFF5F6FA);
  static const Color _userBubble = Color.fromARGB(255, 5, 29, 77);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _surface,
      appBar: AppBar(
        backgroundColor: _primary,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Image.asset(
                "assets/images/logocelcomdigi.png",
                height: 24,
                width: 24,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              "AI-RA by CelcomDigi",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 18,
              ),
            ),
          ],
        ),
      ),
      body: Consumer<ChatViewModel>(
        builder: (context, vm, child) {
          return Column(
            children: [
              // Chat messages
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: vm.messages.length,
                  itemBuilder: (context, index) {
                    final ChatMessage msg = vm.messages[index];

                    return Column(
                      crossAxisAlignment: msg.isUser
                          ? CrossAxisAlignment.end
                          : CrossAxisAlignment.start,
                      children: [
                        // Chat Bubble
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 12),
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          constraints: const BoxConstraints(maxWidth: 320),
                          decoration: BoxDecoration(
                            color: msg.isUser ? _userBubble : Colors.white,
                            borderRadius: BorderRadius.only(
                              topLeft: const Radius.circular(20),
                              topRight: const Radius.circular(20),
                              bottomLeft: Radius.circular(msg.isUser ? 20 : 4),
                              bottomRight: Radius.circular(msg.isUser ? 4 : 20),
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.05),
                                blurRadius: 8,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Text(
                            msg.message,
                            style: TextStyle(
                              color: msg.isUser ? Colors.white : Colors.black87,
                              fontSize: 15,
                              height: 1.4,
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                      ],
                    );
                  },
                ),
              ),

              // Loading indicator
              if (vm.isLoading)
                Container(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                    Colors.blue.shade600),
                              ),
                            ),
                            const SizedBox(width: 12),
                            const Text(
                              "Typing...",
                              style: TextStyle(color: Colors.black54),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

              // Quick actions
              _buildQuickActions(vm),

              // Cards section at the bottom (above input bar)
              // if (vm.messages.any((msg) => msg.cards != null))
              //   Container(
              //     color: Colors.white,
              //     child: _buildPlanSection(
              //       vm.messages
              //           .firstWhere((msg) => msg.cards != null)
              //           .cards!,
              //     ),
              //   ),

              // Input bar
              _buildInputBar(vm),
            ],
          );
        },
      ),
    );
  }

  Widget _buildQuickActions(ChatViewModel vm) {
    final options = [
      ("Login and Registration", Icons.login_rounded),
      ("Account Verification and View All Numbers", Icons.verified_user_outlined),
      ("View or Download Statement", Icons.description_outlined),
      ("Guide to CelcomDigi", Icons.info_outline),
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: options.map((item) {
            final text = item.$1;
            final icon = item.$2;
            return Padding(
              padding: const EdgeInsets.only(right: 10),
              child: InkWell(
                onTap: () => vm.sendMessage(text),
                borderRadius: BorderRadius.circular(18),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: _userBubble,
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                        color: _accent.withOpacity(0.28),
                        blurRadius: 10,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(icon, color: Colors.white, size: 18),
                      const SizedBox(width: 8),
                      Text(
                        text,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  // ================================
  // CARD SECTION UI (Modern Design)
  // ================================
  Widget _buildPlanSection(List<Map<String, String>> cards) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "CelcomDigi Prepaid Plans",
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            "Choose the perfect plan for you",
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 16),

          // Horizontal scrollable cards
          SizedBox(
            height: 220,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: cards.length,
              itemBuilder: (context, index) {
                final item = cards[index];

                return Container(
                  width: 240,
                  margin: const EdgeInsets.only(right: 16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.white,
                        Colors.blue.shade50.withOpacity(0.3),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: Colors.blue.shade100,
                      width: 1.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blue.withOpacity(0.08),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Stack(
                      children: [
                        // Content
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Title
                              Text(
                                item["title"]!,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                  color: Colors.black87,
                                ),
                              ),
                              const SizedBox(height: 8),

                              // Subtitle with badge style
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 10,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      Colors.blue.shade600,
                                      Colors.blue.shade700,
                                    ],
                                  ),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  item["subtitle"]!,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 13,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 12),

                              // Details
                              Expanded(
                                child: Text(
                                  item["details"]!,
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.grey.shade700,
                                    height: 1.4,
                                  ),
                                ),
                              ),

                              // Button
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.blue.shade600,
                                    foregroundColor: Colors.white,
                                    elevation: 0,
                                    padding: const EdgeInsets.symmetric(
                                        vertical: 12),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                  onPressed: () {},
                                  child: const Text(
                                    "View Details",
                                    style: TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),

                        // Decorative gradient accent
                        Positioned(
                          top: 0,
                          right: 0,
                          child: Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.blue.shade200.withOpacity(0.3),
                                  Colors.transparent,
                                ],
                              ),
                              borderRadius: const BorderRadius.only(
                                topRight: Radius.circular(16),
                                bottomLeft: Radius.circular(100),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 16),

          // Compare button
          // Center(
          //   child: OutlinedButton.icon(
          //     style: OutlinedButton.styleFrom(
          //       foregroundColor: Colors.blue.shade700,
          //       side: BorderSide(color: Colors.blue.shade600, width: 1.5),
          //       padding:
          //           const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          //       shape: RoundedRectangleBorder(
          //         borderRadius: BorderRadius.circular(25),
          //       ),
          //     ),
          //     onPressed: () {},
          //     icon: const Icon(Icons.compare_arrows, size: 20),
          //     label: const Text(
          //       "Compare All Plans",
          //       style: TextStyle(
          //         fontWeight: FontWeight.w600,
          //         fontSize: 14,
          //       ),
          //     ),
          //   ),
          // ),
        ],
      ),
    );
  }

  // ================================
  // INPUT BAR (Modern Design)
  // ================================
  Widget _buildInputBar(ChatViewModel vm) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: _surface,
                  borderRadius: BorderRadius.circular(25),
                  border: Border.all(
                    color: Colors.grey.shade300,
                    width: 1,
                  ),
                ),
                child: TextField(
                  controller: _controller,
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                    hintText: "Type your message...",
                    hintStyle: TextStyle(
                      color: Colors.grey.shade500,
                      fontSize: 15,
                    ),
                  ),
                  style: const TextStyle(fontSize: 15),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: BoxDecoration(
                color: _userBubble,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: _accent.withOpacity(0.35),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: IconButton(
                icon: const Icon(Icons.send_rounded, color: Colors.white),
                onPressed: () {
                  if (_controller.text.trim().isNotEmpty) {
                    vm.sendMessage(_controller.text.trim());
                    _controller.clear();
                  }
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}