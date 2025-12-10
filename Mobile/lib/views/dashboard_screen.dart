import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'chat_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  static const Color _primary = Color(0xFF0D47A1);
  static const Color _accent = Color(0xFF2196F3);
  static const Color _lightBlue = Color(0xFF42A5F5);

  void _openChat(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => ChatScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(0),
        child: AppBar(
          backgroundColor: const Color.fromARGB(255, 5, 29, 77),
          elevation: 0,
          systemOverlayStyle: const SystemUiOverlayStyle(
            statusBarColor: const Color.fromARGB(255, 5, 29, 77),
            statusBarIconBrightness: Brightness.light,
            statusBarBrightness: Brightness.dark,
          ),
          toolbarHeight: 0,
        ),
      ),
      backgroundColor: Colors.white,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeaderWithCard(context),
              const SizedBox(height: 20),
              _buildPromoCard(),
              const SizedBox(height: 20),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: const Text(
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
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildHeaderWithCard(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        _buildHeader(bottomPadding: 220),
        Positioned(
          left: 8,
          right: 8,
          bottom: 10,
          child: _buildAccountCard(),
        ),
      ],
    );
  }

  Widget _buildHeader({double bottomPadding = 20}) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.fromLTRB(16, 12, 16, bottomPadding),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color.fromARGB(255, 5, 29, 77),
            const Color.fromARGB(255, 5, 29, 77),
          ],
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
                child: Icon(Icons.person, color: Colors.black, size: 28),
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
              children: [
                Icon(Icons.lock_outline, color: Colors.white, size: 20),
                const SizedBox(width: 10),
                const Text(
                  "Unlock more features with your account",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                const Icon(Icons.arrow_forward_ios,
                    color: Colors.white, size: 16),
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
                    style: TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 15),
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

  Widget _buildPromoCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        height: 140,
        width: double.infinity,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          image: DecorationImage(
            image: NetworkImage(
                'https://celcomdigi.listedcompany.com/images/img/main-banner-mobile.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
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
        BottomNavigationBarItem(icon: Icon(Icons.auto_awesome), label: "For You"),
        BottomNavigationBarItem(icon: Icon(Icons.shield_outlined), label: "Safety"),
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
  final Color color;
  final VoidCallback onTap;

  const _EssentialItem({
    required this.icon,
    required this.label,
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
