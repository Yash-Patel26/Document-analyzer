import 'package:dio/dio.dart';

/// Error handler for API calls
class ErrorHandler {
  static String handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return 'Connection timeout. Please check your internet connection.';
        
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          final message = error.response?.data['detail'] ?? 'An error occurred';
          
          if (statusCode == 401) {
            return 'Authentication failed. Please login again.';
          } else if (statusCode == 403) {
            return 'Access denied.';
          } else if (statusCode == 404) {
            return 'Resource not found.';
          } else if (statusCode == 500) {
            return 'Server error. Please try again later.';
          }
          return message;
        
        case DioExceptionType.cancel:
          return 'Request cancelled.';
        
        case DioExceptionType.unknown:
          return 'Network error. Please check your connection.';
        
        default:
          return 'An unexpected error occurred.';
      }
    }
    
    return error.toString();
  }
}

