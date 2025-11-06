import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants.dart';
import 'api_client.dart';

class AuthService {
  final ApiClient _apiClient;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  AuthService(this._apiClient);

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _apiClient.post(
      '/auth/login',
      data: {
        'username': username,
        'password': password,
      },
    );

    final tokens = response.data as Map<String, dynamic>;
    
    // Store tokens
    await _storage.write(
      key: AppConstants.accessTokenKey,
      value: tokens['access_token'],
    );
    await _storage.write(
      key: AppConstants.refreshTokenKey,
      value: tokens['refresh_token'],
    );

    return tokens;
  }

  Future<void> logout() async {
    try {
      await _apiClient.post('/auth/logout');
    } catch (e) {
      // Continue with logout even if API call fails
    } finally {
      await _storage.deleteAll();
    }
  }

  Future<Map<String, dynamic>?> getCurrentUser() async {
    try {
      final response = await _apiClient.get('/auth/me');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  Future<bool> isAuthenticated() async {
    final token = await _storage.read(key: AppConstants.accessTokenKey);
    return token != null && token.isNotEmpty;
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: AppConstants.accessTokenKey);
  }
}

