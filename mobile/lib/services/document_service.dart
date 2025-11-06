import '../core/constants.dart';
import 'api_client.dart';
import 'dart:io';

class DocumentService {
  final ApiClient _apiClient;

  DocumentService(this._apiClient);

  Future<Map<String, dynamic>> uploadDocument(File file) async {
    final response = await _apiClient.uploadFile(
      '/upload/',
      file.path,
      file.path.split('/').last,
    );

    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getJobStatus(String jobId) async {
    final response = await _apiClient.get('/jobs/$jobId');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getJobResult(String jobId) async {
    final response = await _apiClient.get('/jobs/$jobId/result');
    return response.data as Map<String, dynamic>;
  }

  Future<void> triggerAnalysis(String jobId) async {
    await _apiClient.post('/jobs/$jobId/analyze');
  }

  Future<String> exportReport(String jobId, String format) async {
    final response = await _apiClient.downloadFile(
      '/jobs/$jobId/export?format=$format',
      '/tmp/report.$format',
    );
    return response.data.toString();
  }
}

