// import 'package:flutter/foundation.dart';
// import 'package:flutter/material.dart';
// import 'package:flutter/services.dart';

// import 'chat_screen.dart';

// class DashboardScreen extends StatelessWidget {
//   const DashboardScreen({super.key});

//   static const Color _primary = Color(0xFF0D47A1);
//   static const Color _accent = Color(0xFF2196F3);
//   void _openChat(BuildContext context) {
//     Navigator.of(context).push(
//       MaterialPageRoute(builder: (_) => ChatScreen()),
//     );
//   }

//   @override
//   Widget build(BuildContext context) {
//     return LayoutBuilder(
//       builder: (context, constraints) {
//         final isWideWeb = kIsWeb && constraints.maxWidth >= 900;
//         final horizontalPadding = isWideWeb ? 32.0 : 16.0;
//         final headerBottomPadding = isWideWeb ? 180.0 : 220.0;
//         final gridCrossAxisCount = isWideWeb ? 6 : 4;
//         final promoHeight = isWideWeb ? 180.0 : 140.0;
//         final gridAspectRatio = isWideWeb ? 1.0 : 0.85;
//         final backgroundColor =
//             isWideWeb ? const Color(0xFFF5F7FB) : Colors.white;

//         return Scaffold(
//           appBar: PreferredSize(
//             preferredSize: const Size.fromHeight(0),
//             child: AppBar(
//               backgroundColor: const Color.fromARGB(255, 5, 29, 77),
//               elevation: 0,
//               systemOverlayStyle: const SystemUiOverlayStyle(
//                 statusBarColor: const Color.fromARGB(255, 5, 29, 77),
//                 statusBarIconBrightness: Brightness.light,
//                 statusBarBrightness: Brightness.dark,
//               ),
//               toolbarHeight: 0,
//             ),
//           ),
//           backgroundColor: backgroundColor,
//           body: SafeArea(
//             child: SingleChildScrollView(
//               child: Center(
//                 child: ConstrainedBox(
//                   constraints: BoxConstraints(
//                     maxWidth: isWideWeb ? 1100 : double.infinity,
//                   ),
//                   child: Column(
//                     crossAxisAlignment: CrossAxisAlignment.start,
//                     children: [
//                       _buildHeaderWithCard(
//                         context,
//                         horizontalPadding: horizontalPadding,
//                         bottomPadding: headerBottomPadding,
//                         elevated: isWideWeb,
//                       ),
//                       const SizedBox(height: 20),
//                       _buildPromoCard(
//                         horizontalPadding: horizontalPadding,
//                         height: promoHeight,
//                         elevated: isWideWeb,
//                       ),
//                       const SizedBox(height: 20),
//                       Padding(
//                         padding: EdgeInsets.symmetric(
//                           horizontal: horizontalPadding,
//                         ),
//                         child: const Text(
//                           "Your Essentials",
//                           style: TextStyle(
//                             fontSize: 20,
//                             fontWeight: FontWeight.bold,
//                             color: Colors.black,
//                           ),
//                         ),
//                       ),
//                       const SizedBox(height: 16),
//                       _buildEssentialsGrid(
//                         context,
//                         horizontalPadding: horizontalPadding,
//                         crossAxisCount: gridCrossAxisCount,
//                         childAspectRatio: gridAspectRatio,
//                       ),
//                       const SizedBox(height: 24),
//                     ],
//                   ),
//                 ),
//               ),
//             ),
//           ),
//           bottomNavigationBar: isWideWeb ? null : _buildBottomNav(),
//         );
//       },
//     );
//   }

//   Widget _buildHeaderWithCard(
//     BuildContext context, {
//     double horizontalPadding = 16,
//     double bottomPadding = 220,
//     bool elevated = false,
//   }) {
//     return Stack(
//       clipBehavior: Clip.none,
//       children: [
//         _buildHeader(
//           bottomPadding: bottomPadding,
//           horizontalPadding: horizontalPadding,
//         ),
//         Positioned(
//           left: horizontalPadding / 2,
//           right: horizontalPadding / 2,
//           bottom: 10,
//           child: _buildAccountCard(
//             horizontalPadding: horizontalPadding,
//             elevated: elevated,
//           ),
//         ),
//       ],
//     );
//   }

//   Widget _buildHeader({
//     double bottomPadding = 20,
//     double horizontalPadding = 16,
//   }) {
//     return Container(
//       width: double.infinity,
//       padding: EdgeInsets.fromLTRB(
//         horizontalPadding,
//         12,
//         horizontalPadding,
//         bottomPadding,
//       ),
//       decoration: const BoxDecoration(
//         gradient: LinearGradient(
//           colors: [
//             const Color.fromARGB(255, 5, 29, 77),
//             const Color.fromARGB(255, 5, 29, 77),
//           ],
//           begin: Alignment.topCenter,
//           end: Alignment.bottomCenter,
//         ),
//       ),
//       child: Column(
//         crossAxisAlignment: CrossAxisAlignment.start,
//         children: [
//           Row(
//             children: [
//               CircleAvatar(
//                 radius: 24,
//                 backgroundColor: Colors.yellow.shade700,
//                 child: Icon(Icons.person, color: Colors.black, size: 28),
//               ),
//               const SizedBox(width: 12),
//               Expanded(
//                 child: Column(
//                   crossAxisAlignment: CrossAxisAlignment.start,
//                   children: const [
//                     Text(
//                       "Hello, how are you?",
//                       style: TextStyle(
//                         color: Colors.white,
//                         fontSize: 18,
//                         fontWeight: FontWeight.bold,
//                       ),
//                     ),
//                     SizedBox(height: 2),
//                     Text(
//                       "Tharani",
//                       style: TextStyle(
//                         color: Colors.white70,
//                         fontSize: 14,
//                       ),
//                     ),
//                   ],
//                 ),
//               ),
//               IconButton(
//                 onPressed: () {},
//                 icon: const Icon(Icons.settings_outlined, color: Colors.white),
//               ),
//               Stack(
//                 children: [
//                   IconButton(
//                     onPressed: () {},
//                     icon: const Icon(Icons.notifications_outlined,
//                         color: Colors.white),
//                   ),
//                   Positioned(
//                     right: 10,
//                     top: 10,
//                     child: Container(
//                       width: 8,
//                       height: 8,
//                       decoration: const BoxDecoration(
//                         color: Colors.red,
//                         shape: BoxShape.circle,
//                       ),
//                     ),
//                   ),
//                 ],
//               ),
//             ],
//           ),
//           const SizedBox(height: 16),
//           Container(
//             padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
//             decoration: BoxDecoration(
//               color: Colors.white.withOpacity(0.2),
//               borderRadius: BorderRadius.circular(12),
//             ),
//             child: Row(
//               children: [
//                 Icon(Icons.lock_outline, color: Colors.white, size: 20),
//                 const SizedBox(width: 10),
//                 const Text(
//                   "Unlock more features with your account",
//                   style: TextStyle(
//                     color: Colors.white,
//                     fontSize: 14,
//                     fontWeight: FontWeight.w500,
//                   ),
//                 ),
//                 const Spacer(),
//                 const Icon(Icons.arrow_forward_ios,
//                     color: Colors.white, size: 16),
//               ],
//             ),
//           ),
//         ],
//       ),
//     );
//   }

//   Widget _buildAccountCard({
//     double horizontalPadding = 16,
//     bool elevated = false,
//   }) {
//     return Padding(
//       padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
//       child: Container(
//         padding: const EdgeInsets.all(16),
//         decoration: BoxDecoration(
//           color: const Color(0xFFE3F2FD),
//           borderRadius: BorderRadius.circular(16),
//           boxShadow: elevated
//               ? [
//                   BoxShadow(
//                     color: Colors.black.withOpacity(0.08),
//                     blurRadius: 18,
//                     offset: const Offset(0, 10),
//                   ),
//                 ]
//               : null,
//         ),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             Row(
//               children: [
//                 Container(
//                   padding:
//                       const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
//                   decoration: BoxDecoration(
//                     color: Colors.green.shade100,
//                     borderRadius: BorderRadius.circular(20),
//                   ),
//                   child: Row(
//                     children: const [
//                       Icon(Icons.check_circle, color: Colors.green, size: 16),
//                       SizedBox(width: 4),
//                       Text(
//                         "Active",
//                         style: TextStyle(
//                           color: Colors.green,
//                           fontWeight: FontWeight.w600,
//                           fontSize: 13,
//                         ),
//                       ),
//                     ],
//                   ),
//                 ),
//                 const Spacer(),
//                 TextButton(
//                   onPressed: () {},
//                   style: TextButton.styleFrom(
//                     foregroundColor: _primary,
//                   ),
//                   child: Row(
//                     children: const [
//                       Text(
//                         "My Numbers",
//                         style: TextStyle(fontWeight: FontWeight.w600),
//                       ),
//                       SizedBox(width: 4),
//                       Icon(Icons.arrow_forward_ios, size: 14),
//                     ],
//                   ),
//                 ),
//               ],
//             ),
//             const SizedBox(height: 16),
//             const Text(
//               "Balance:",
//               style: TextStyle(
//                 color: Colors.black87,
//                 fontSize: 14,
//               ),
//             ),
//             const SizedBox(height: 4),
//             Row(
//               crossAxisAlignment: CrossAxisAlignment.end,
//               children: [
//                 const Text(
//                   "RM 32.00",
//                   style: TextStyle(
//                     color: Colors.black,
//                     fontSize: 32,
//                     fontWeight: FontWeight.bold,
//                   ),
//                 ),
//                 const Spacer(),
//                 ElevatedButton(
//                   style: ElevatedButton.styleFrom(
//                     backgroundColor: _accent,
//                     foregroundColor: Colors.white,
//                     shape: RoundedRectangleBorder(
//                       borderRadius: BorderRadius.circular(24),
//                     ),
//                     padding: const EdgeInsets.symmetric(
//                         horizontal: 32, vertical: 12),
//                   ),
//                   onPressed: () {},
//                   child: const Text(
//                     "Reload",
//                     style: TextStyle(
//                         fontWeight: FontWeight.bold, fontSize: 15),
//                   ),
//                 ),
//               ],
//             ),
//             const SizedBox(height: 8),
//             Text(
//               "Reload by 13/02/2026",
//               style: TextStyle(
//                 color: Colors.grey.shade700,
//                 fontSize: 13,
//               ),
//             ),
//           ],
//         ),
//       ),
//     );
//   }

//   Widget _buildPromoCard({
//     double horizontalPadding = 16,
//     double height = 140,
//     bool elevated = false,
//   }) {
//     return Padding(
//       padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
//       child: DecoratedBox(
//         decoration: BoxDecoration(
//           borderRadius: BorderRadius.circular(16),
//           boxShadow: elevated
//               ? [
//                   BoxShadow(
//                     color: Colors.black.withOpacity(0.06),
//                     blurRadius: 16,
//                     offset: const Offset(0, 8),
//                   ),
//                 ]
//               : null,
//         ),
//         child: ClipRRect(
//           borderRadius: BorderRadius.circular(16),
//           child: Container(
//             height: height,
//             width: double.infinity,
//             decoration: const BoxDecoration(
//               image: DecorationImage(
//                 image: NetworkImage(
//                     'https://celcomdigi.listedcompany.com/images/img/main-banner-mobile.png'),
//                 fit: BoxFit.cover,
//               ),
//             ),
//             child: Container(
//               decoration: BoxDecoration(
//                 gradient: LinearGradient(
//                   colors: [
//                     Colors.black.withOpacity(0.3),
//                     Colors.transparent,
//                   ],
//                   begin: Alignment.topRight,
//                   end: Alignment.centerRight,
//                 ),
//               ),
//               padding: const EdgeInsets.all(20),
//               child: Column(
//                 crossAxisAlignment: CrossAxisAlignment.end,
//                 mainAxisAlignment: MainAxisAlignment.center,
//                 children: const [
//                   Text(
//                     "Stress-free travel",
//                     textAlign: TextAlign.right,
//                     style: TextStyle(
//                       color: Colors.white,
//                       fontSize: 20,
//                       fontWeight: FontWeight.bold,
//                     ),
//                   ),
//                   SizedBox(height: 4),
//                   Text(
//                     "with pre-book",
//                     textAlign: TextAlign.right,
//                     style: TextStyle(
//                       color: Colors.white,
//                       fontSize: 20,
//                       fontWeight: FontWeight.bold,
//                     ),
//                   ),
//                   SizedBox(height: 4),
//                   Text(
//                     "roaming",
//                     textAlign: TextAlign.right,
//                     style: TextStyle(
//                       color: Colors.white,
//                       fontSize: 20,
//                       fontWeight: FontWeight.bold,
//                     ),
//                   ),
//                 ],
//               ),
//             ),
//           ),
//         ),
//       ),
//     );
//   }

//   Widget _buildEssentialsGrid(
//     BuildContext context, {
//     double horizontalPadding = 16,
//     int crossAxisCount = 4,
//     double childAspectRatio = 0.85,
//   }) {
//     final items = [
//       _EssentialItem(
//         icon: Icons.language,
//         label: "Usage",
//         color: const Color(0xFF2196F3),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.account_balance_wallet,
//         label: "Check\nBalance",
//         color: const Color(0xFF2196F3),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.sim_card,
//         label: "My Plan",
//         color: const Color(0xFFFFA726),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.smart_toy,
//         label: "Ask AI-RA",
//         color: const Color(0xFF42A5F5),
//         onTap: () => _openChat(context),
//       ),
//       _EssentialItem(
//         icon: Icons.person,
//         label: "Profile",
//         color: const Color(0xFF5C6BC0),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.public,
//         label: "Roaming",
//         color: const Color(0xFF42A5F5),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.card_giftcard,
//         label: "Rewards",
//         color: const Color(0xFFEC407A),
//         onTap: () {},
//       ),
//       _EssentialItem(
//         icon: Icons.apps,
//         label: "More",
//         color: const Color(0xFF5C6BC0),
//         onTap: () {},
//       ),
//     ];

//     return Padding(
//       padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
//       child: GridView.builder(
//         itemCount: items.length,
//         shrinkWrap: true,
//         physics: const NeverScrollableScrollPhysics(),
//         gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
//           crossAxisCount: crossAxisCount,
//           mainAxisSpacing: 20,
//           crossAxisSpacing: 16,
//           childAspectRatio: childAspectRatio,
//         ),
//         itemBuilder: (_, index) {
//           final item = items[index];
//           return _EssentialTile(item: item);
//         },
//       ),
//     );
//   }

//   Widget _buildBottomNav() {
//     return BottomNavigationBar(
//       currentIndex: 0,
//       selectedItemColor: _primary,
//       unselectedItemColor: Colors.grey.shade600,
//       showUnselectedLabels: true,
//       type: BottomNavigationBarType.fixed,
//       items: const [
//         BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
//         BottomNavigationBarItem(
//             icon: Icon(Icons.shopping_bag_outlined), label: "Shop"),
//         BottomNavigationBarItem(icon: Icon(Icons.auto_awesome), label: "For You"),
//         BottomNavigationBarItem(icon: Icon(Icons.shield_outlined), label: "Safety"),
//         BottomNavigationBarItem(
//             icon: Icon(Icons.headset_mic_outlined), label: "Support"),
//       ],
//       onTap: (_) {},
//     );
//   }
// }

// class _EssentialItem {
//   final IconData icon;
//   final String label;
//   final Color color;
//   final VoidCallback onTap;

//   const _EssentialItem({
//     required this.icon,
//     required this.label,
//     required this.color,
//     required this.onTap,
//   });
// }

// class _EssentialTile extends StatelessWidget {
//   final _EssentialItem item;

//   const _EssentialTile({required this.item});

//   @override
//   Widget build(BuildContext context) {
//     return InkWell(
//       onTap: item.onTap,
//       borderRadius: BorderRadius.circular(12),
//       child: Column(
//         mainAxisAlignment: MainAxisAlignment.center,
//         children: [
//           Container(
//             width: 56,
//             height: 56,
//             padding: const EdgeInsets.all(12),
//             decoration: BoxDecoration(
//               color: item.color.withOpacity(0.15),
//               borderRadius: BorderRadius.circular(16),
//             ),
//             child: Icon(
//               item.icon,
//               color: item.color,
//               size: 28,
//             ),
//           ),
//           const SizedBox(height: 8),
//           Text(
//             item.label,
//             textAlign: TextAlign.center,
//             style: const TextStyle(
//               fontSize: 11,
//               fontWeight: FontWeight.w500,
//               color: Colors.black87,
//               height: 1.2,
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'chat_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  static const Color _primary = Color(0xFF0D47A1);
  static const Color _accent = Color(0xFF2196F3);
  static const Color _darkBlue = Color.fromARGB(255, 5, 29, 77);

  void _openChat(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => ChatScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWideWeb = kIsWeb && constraints.maxWidth >= 900;

        return Scaffold(
          appBar: isWideWeb ? null : _buildMobileAppBar(),
          backgroundColor: isWideWeb ? const Color(0xFFF8F9FA) : Colors.white,
          body: isWideWeb ? _buildWebLayout(context) : _buildMobileLayout(context),
          bottomNavigationBar: isWideWeb ? null : _buildBottomNav(),
        );
      },
    );
  }

  // ========== WEB LAYOUT ==========
  Widget _buildWebLayout(BuildContext context) {
    return Column(
      children: [
        _buildWebHeader(context),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 40),
                _buildWebContent(context),
                const SizedBox(height: 60),
                _buildWebFooter(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWebHeader(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 60, vertical: 20),
      child: Row(
        children: [
          // Logo/Brand
          Row(
            children: [
Container(
  width: 40,
  height: 40,
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(10),
  ),
  child: Padding(
    padding: const EdgeInsets.all(6.0), // adjust to fit nicely
    child: Image.asset(
      'assets/images/logocelcomdigi.png',
      fit: BoxFit.contain,
    ),
  ),
),

              const SizedBox(width: 12),
              const Text(
                "celcomdigi",
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color.fromARGB(255, 5, 29, 77),
                ),
              ),
            ],
          ),
          const Spacer(),
          // Navigation Menu
          _buildNavLink("Home", true),
          const SizedBox(width: 32),
          _buildNavLink("Plans", false),
          const SizedBox(width: 32),
          _buildNavLink("Roaming", false),
          const SizedBox(width: 32),
          _buildNavLink("Support", false),
          const SizedBox(width: 40),
          // User Section
          Stack(
            children: [
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.notifications_outlined),
                color: Colors.grey.shade700,
              ),
              Positioned(
                right: 8,
                top: 8,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            radius: 20,
            backgroundColor: Colors.yellow.shade700,
            child: const Icon(Icons.person, color: Colors.black, size: 24),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text(
                "Tharani",
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
              Text(
                "Active Plan",
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNavLink(String label, bool isActive) {
    return TextButton(
      onPressed: () {},
      style: TextButton.styleFrom(
        foregroundColor: isActive ? _primary : Colors.grey.shade700,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 15,
          fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildWebContent(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1200),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 60),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 2,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "Hello, Tharani! 👋",
                          style: TextStyle(
                            fontSize: 36,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          "Welcome back to your dashboard. Manage your account, check usage, and explore new features.",
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey.shade700,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 32),
                        _buildWebAccountCard(),
                      ],
                    ),
                  ),
                  const SizedBox(width: 40),
                  Expanded(
                    child: _buildWebPromoCard(),
                  ),
                ],
              ),
              const SizedBox(height: 60),
              // Quick Actions Section
              const Text(
                "Quick Actions",
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 24),
              _buildWebQuickActions(context),
              const SizedBox(height: 60),
              // Features Banner
              _buildWebFeaturesBanner(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWebAccountCard() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_darkBlue, _primary],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: _primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green.shade400,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: const [
                    Icon(Icons.check_circle, color: Colors.white, size: 16),
                    SizedBox(width: 4),
                    Text(
                      "Active",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: () {},
                style: TextButton.styleFrom(
                  foregroundColor: Colors.white,
                ),
                icon: const Text(
                  "My Numbers",
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                label: const Icon(Icons.arrow_forward, size: 18),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Text(
            "Current Balance",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "RM 32.00",
            style: TextStyle(
              color: Colors.white,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: _primary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () {},
                  icon: const Icon(Icons.add_circle_outline),
                  label: const Text(
                    "Reload Now",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              OutlinedButton(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white70),
                  padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: () {},
                child: const Text("View Usage"),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            "⏰ Reload by 13/02/2026",
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWebPromoCard() {
    return Container(
      height: 400,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: Container(
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/main-banner-mobile.png'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.black.withOpacity(0.4),
                  Colors.transparent,
                ],
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
              ),
            ),
            padding: const EdgeInsets.all(32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Text(
                  "Stress-free travel\nwith pre-book\nroaming",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: _primary,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  onPressed: () {},
                  child: const Text(
                    "Learn More",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWebQuickActions(BuildContext context) {
    final items = [
      _EssentialItem(
        icon: Icons.language,
        label: "Check Usage",
        description: "View your data and call usage",
        color: const Color(0xFF2196F3),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.account_balance_wallet,
        label: "Check Balance",
        description: "View account balance details",
        color: const Color(0xFF2196F3),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.sim_card,
        label: "My Plan",
        description: "Manage your current plan",
        color: const Color(0xFFFFA726),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.smart_toy,
        label: "Ask AI-RA",
        description: "Get instant AI assistance",
        color: const Color(0xFF42A5F5),
        onTap: () => _openChat(context),
      ),
      _EssentialItem(
        icon: Icons.public,
        label: "Roaming",
        description: "Manage roaming services",
        color: const Color(0xFF42A5F5),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.card_giftcard,
        label: "Rewards",
        description: "View your rewards & offers",
        color: const Color(0xFFEC407A),
        onTap: () {},
      ),
    ];

    return GridView.builder(
      itemCount: items.length,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 20,
        crossAxisSpacing: 20,
        childAspectRatio: 1.8,
      ),
      itemBuilder: (_, index) {
        final item = items[index];
        return _buildWebActionCard(item);
      },
    );
  }

  Widget _buildWebActionCard(_EssentialItem item) {
    return InkWell(
      onTap: item.onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: item.color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                item.icon,
                color: item.color,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    item.label,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item.description ?? '',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: Colors.grey.shade400,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWebFeaturesBanner() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 40),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_accent.withOpacity(0.1), _primary.withOpacity(0.05)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _accent.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(Icons.lock_outline, size: 48, color: _primary),
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Unlock Premium Features",
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  "Upgrade your account to access exclusive benefits, faster speeds, and priority support.",
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: _primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            onPressed: () {},
            child: const Text(
              "Explore Plans",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWebFooter() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 60, vertical: 40),
      decoration: BoxDecoration(
        color: _darkBlue,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "celcomdigi",
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      "Your trusted telecommunications partner",
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.7),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              _buildFooterColumn("Services", [
                "Mobile Plans",
                "Roaming",
                "Reload",
                "Rewards",
              ]),
              _buildFooterColumn("Support", [
                "Help Center",
                "Contact Us",
                "FAQ",
                "Live Chat",
              ]),
              _buildFooterColumn("Company", [
                "About Us",
                "Careers",
                "Privacy Policy",
                "Terms of Service",
              ]),
            ],
          ),
          const SizedBox(height: 32),
          Divider(color: Colors.white.withOpacity(0.2)),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "© 2025 celcomdigi. All rights reserved.",
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 13,
                ),
              ),
              Row(
                children: [
                  IconButton(
                    onPressed: () {},
                    icon: Icon(Icons.facebook, color: Colors.white.withOpacity(0.7)),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(Icons.link, color: Colors.white.withOpacity(0.7)),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(Icons.telegram, color: Colors.white.withOpacity(0.7)),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFooterColumn(String title, List<String> links) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ...links.map((link) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: InkWell(
                  onTap: () {},
                  child: Text(
                    link,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 14,
                    ),
                  ),
                ),
              )),
        ],
      ),
    );
  }

  // ========== MOBILE LAYOUT (ORIGINAL) ==========
  Widget _buildMobileLayout(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeaderWithCard(context),
            const SizedBox(height: 20),
            _buildPromoCard(horizontalPadding: 16),
            const SizedBox(height: 20),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                "Your Essentials",
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                ),
              ),
            ),
            const SizedBox(height: 16),
            _buildEssentialsGrid(context),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  PreferredSizeWidget _buildMobileAppBar() {
    return PreferredSize(
      preferredSize: const Size.fromHeight(0),
      child: AppBar(
        backgroundColor: _darkBlue,
        elevation: 0,
        systemOverlayStyle: SystemUiOverlayStyle(
          statusBarColor: _darkBlue,
          statusBarIconBrightness: Brightness.light,
          statusBarBrightness: Brightness.dark,
        ),
        toolbarHeight: 0,
      ),
    );
  }

  Widget _buildHeaderWithCard(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        _buildHeader(),
        Positioned(
          left: 8,
          right: 8,
          bottom: 10,
          child: _buildAccountCard(),
        ),
      ],
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 220),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_darkBlue, _darkBlue],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 24,
                backgroundColor: Colors.yellow.shade700,
                child: const Icon(Icons.person, color: Colors.black, size: 28),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text(
                      "Hello, how are you?",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      "Tharani",
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.settings_outlined, color: Colors.white),
              ),
              Stack(
                children: [
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(Icons.notifications_outlined,
                        color: Colors.white),
                  ),
                  Positioned(
                    right: 10,
                    top: 10,
                    child: Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: const [
                Icon(Icons.lock_outline, color: Colors.white, size: 20),
                SizedBox(width: 10),
                Text(
                  "Unlock more features with your account",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Spacer(),
                Icon(Icons.arrow_forward_ios, color: Colors.white, size: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAccountCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFFE3F2FD),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.shade100,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: const [
                      Icon(Icons.check_circle, color: Colors.green, size: 16),
                      SizedBox(width: 4),
                      Text(
                        "Active",
                        style: TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {},
                  style: TextButton.styleFrom(
                    foregroundColor: _primary,
                  ),
                  child: Row(
                    children: const [
                      Text(
                        "My Numbers",
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      SizedBox(width: 4),
                      Icon(Icons.arrow_forward_ios, size: 14),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              "Balance:",
              style: TextStyle(
                color: Colors.black87,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                const Text(
                  "RM 32.00",
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _accent,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 32, vertical: 12),
                  ),
                  onPressed: () {},
                  child: const Text(
                    "Reload",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              "Reload by 13/02/2026",
              style: TextStyle(
                color: Colors.grey.shade700,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPromoCard({double horizontalPadding = 16}) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Container(
          height: 140,
          width: double.infinity,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/main-banner-mobile.png'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.black.withOpacity(0.3),
                  Colors.transparent,
                ],
                begin: Alignment.topRight,
                end: Alignment.centerRight,
              ),
            ),
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                Text(
                  "Stress-free travel",
                  textAlign: TextAlign.right,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  "with pre-book",
                  textAlign: TextAlign.right,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  "roaming",
                  textAlign: TextAlign.right,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEssentialsGrid(BuildContext context) {
    final items = [
      _EssentialItem(
        icon: Icons.language,
        label: "Usage",
        color: const Color(0xFF2196F3),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.account_balance_wallet,
        label: "Check\nBalance",
        color: const Color(0xFF2196F3),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.sim_card,
        label: "My Plan",
        color: const Color(0xFFFFA726),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.smart_toy,
        label: "Ask AI-RA",
        color: const Color(0xFF42A5F5),
        onTap: () => _openChat(context),
      ),
      _EssentialItem(
        icon: Icons.person,
        label: "Profile",
        color: const Color(0xFF5C6BC0),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.public,
        label: "Roaming",
        color: const Color(0xFF42A5F5),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.card_giftcard,
        label: "Rewards",
        color: const Color(0xFFEC407A),
        onTap: () {},
      ),
      _EssentialItem(
        icon: Icons.apps,
        label: "More",
        color: const Color(0xFF5C6BC0),
        onTap: () {},
      ),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: GridView.builder(
        itemCount: items.length,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 4,
          mainAxisSpacing: 20,
          crossAxisSpacing: 16,
          childAspectRatio: 0.85,
        ),
        itemBuilder: (_, index) {
          final item = items[index];
          return _EssentialTile(item: item);
        },
      ),
    );
  }

  Widget _buildBottomNav() {
    return BottomNavigationBar(
      currentIndex: 0,
      selectedItemColor: _primary,
      unselectedItemColor: Colors.grey.shade600,
      showUnselectedLabels: true,
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.home), label: "Home"),
        BottomNavigationBarItem(
            icon: Icon(Icons.shopping_bag_outlined), label: "Shop"),
        BottomNavigationBarItem(
            icon: Icon(Icons.auto_awesome), label: "For You"),
        BottomNavigationBarItem(
            icon: Icon(Icons.shield_outlined), label: "Safety"),
        BottomNavigationBarItem(
            icon: Icon(Icons.headset_mic_outlined), label: "Support"),
      ],
      onTap: (_) {},
    );
  }
}

class _EssentialItem {
  final IconData icon;
  final String label;
  final String? description;
  final Color color;
  final VoidCallback onTap;

  const _EssentialItem({
    required this.icon,
    required this.label,
    this.description,
    required this.color,
    required this.onTap,
  });
}

class _EssentialTile extends StatelessWidget {
  final _EssentialItem item;

  const _EssentialTile({required this.item});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: item.onTap,
      borderRadius: BorderRadius.circular(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 56,
            height: 56,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: item.color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(
              item.icon,
              color: item.color,
              size: 28,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            item.label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: Colors.black87,
              height: 1.2,
            ),
          ),
        ],
      ),
    );
  }
}