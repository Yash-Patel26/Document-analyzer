import '../core/constants.dart';
import 'api_client.dart';

class FeedbackService {
  final ApiClient _apiClient;

  FeedbackService(this._apiClient);

  Future<void> submitSummaryFeedback({
    required String jobId,
    int? rating,
    bool? isCorrect,
    String? correctedSummary,
  }) async {
    await _apiClient.post(
      '/feedback/summary',
      data: {
        'job_id': jobId,
        'summary_rating': rating,
        'is_correct': isCorrect,
        'corrected_summary': correctedSummary,
      },
    );
  }

  Future<void> submitEntityCorrections({
    required String jobId,
    required List<Map<String, dynamic>> corrections,
  }) async {
    await _apiClient.post('/feedback/entities/$jobId', data: corrections);
  }

  Future<void> submitQAFeedback({
    required int messageId,
    int? rating,
    bool? isCorrect,
    String? correctedAnswer,
  }) async {
    await _apiClient.post(
      '/feedback/qa',
      data: {
        'message_id': messageId,
        'answer_rating': rating,
        'is_correct': isCorrect,
        'corrected_answer': correctedAnswer,
      },
    );
  }
}
