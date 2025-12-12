/// App Configuration
/// 
/// Centralized configuration for the app.
/// For production, these values should come from environment variables
/// or a secure configuration management system.
/// 
/// Usage:
///   import 'package:let_it_fly/config/app_config.dart';
///   final url = AppConfig.apiBaseUrl;

class AppConfig {
  // Private constructor to prevent instantiation
  AppConfig._();

  /// API Configuration
  /// In production, consider using:
  /// - flutter_dotenv package with .env file
  /// - --dart-define flags during build
  /// - Remote config service
  
  /// Chat API base URL
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://bteng7ing0.execute-api.ap-southeast-1.amazonaws.com/prod/chat',
  );
  
  /// API timeout in seconds
  static const int apiTimeout = 30;
  
  /// Enable debug logging
  static const bool debugMode = bool.fromEnvironment(
    'DEBUG_MODE',
    defaultValue: false,
  );

  /// External Resources
  static const String bannerImageUrl = 'https://celcomdigi.listedcompany.com/images/img/main-banner-mobile.png';
  
  /// Customer Support
  static const String supportHotline = '100';
  static const String supportEmail = 'support@celcomdigi.com';
}

