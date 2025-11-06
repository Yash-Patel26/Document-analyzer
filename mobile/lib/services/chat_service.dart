import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_client.dart';

class ChatService {
  final ApiClient _apiClient;
  WebSocketChannel? _channel;
  StreamController<String>? _messageController;

  ChatService(this._apiClient);

  Future<Map<String, dynamic>> sendMessage(String jobId, String message) async {
    final response = await _apiClient.post(
      '/jobs/$jobId/chat',
      data: {'message': message},
    );

    return response.data as Map<String, dynamic>;
  }

  Stream<String> sendMessageStream(String jobId, String message) {
    _messageController = StreamController<String>();
    
    // For now, use SSE simulation via polling
    // In production, use WebSocket connection
    _simulateStreaming(jobId, message);
    
    return _messageController!.stream;
  }

  void _simulateStreaming(String jobId, String message) async {
    try {
      final response = await sendMessage(jobId, message);
      final answer = response['answer'] as String? ?? '';
      
      // Simulate streaming by sending chunks
      final words = answer.split(' ');
      for (var word in words) {
        _messageController?.add('$word ');
        await Future.delayed(const Duration(milliseconds: 50));
      }
      _messageController?.close();
    } catch (e) {
      _messageController?.addError(e);
    }
  }

  Future<List<Map<String, dynamic>>> getChatHistory(String jobId) async {
    final response = await _apiClient.get('/jobs/$jobId/chat/history');
    return List<Map<String, dynamic>>.from(response.data);
  }

  void dispose() {
    _channel?.sink.close();
    _messageController?.close();
  }
}

