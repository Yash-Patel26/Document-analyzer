import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../services/document_service.dart';
import '../services/chat_service.dart';
import '../services/feedback_service.dart';

// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// Auth Service Provider
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref.read(apiClientProvider));
});

// Document Service Provider
final documentServiceProvider = Provider<DocumentService>((ref) {
  return DocumentService(ref.read(apiClientProvider));
});

// Chat Service Provider
final chatServiceProvider = Provider<ChatService>((ref) {
  return ChatService(ref.read(apiClientProvider));
});

// Feedback Service Provider
final feedbackServiceProvider = Provider<FeedbackService>((ref) {
  return FeedbackService(ref.read(apiClientProvider));
});
