/// Application constants
class AppConstants {
  // API Configuration
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'user';
  
  // Database
  static const String databaseName = 'analyzer.db';
  static const int databaseVersion = 1;
  
  // File Upload
  static const int maxFileSize = 100 * 1024 * 1024; // 100MB
  static const List<String> allowedExtensions = [
    '.pdf',
    '.docx',
    '.txt',
    '.jpg',
    '.jpeg',
    '.png',
  ];
  
  // Retry Configuration
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);
  
  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}

