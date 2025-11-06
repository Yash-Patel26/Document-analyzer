import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../services/document_service.dart';
import '../../../services/feedback_service.dart';
import '../../../providers/api_provider.dart';
import 'feedback_widget.dart';

class DocumentResultScreen extends ConsumerStatefulWidget {
  final String jobId;

  const DocumentResultScreen({super.key, required this.jobId});

  @override
  ConsumerState<DocumentResultScreen> createState() =>
      _DocumentResultScreenState();
}

class _DocumentResultScreenState extends ConsumerState<DocumentResultScreen> {
  Map<String, dynamic>? _result;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadResult();
  }

  Future<void> _loadResult() async {
    try {
      final documentService = ref.read(documentServiceProvider);
      final result = await documentService.getJobResult(widget.jobId);
      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _showFeedbackDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => FeedbackWidget(
        jobId: widget.jobId,
        type: 'summary',
        onFeedbackSubmitted: (feedback) async {
          // Submit feedback to API
          try {
            final feedbackService = ref.read(feedbackServiceProvider);
            await feedbackService.submitSummaryFeedback(
              jobId: widget.jobId,
              rating: feedback['rating'] as int?,
              isCorrect: feedback['is_correct'] as bool?,
              correctedSummary: feedback['correction'] as String?,
            );
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'Thank you for your feedback! It will help improve the models.',
                  ),
                ),
              );
            }
          } catch (e) {
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error submitting feedback: $e')),
              );
            }
          }
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Analysis Results')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Analysis Results')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('Error: $_error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadResult,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Results'),
        actions: [
          IconButton(
            icon: const Icon(Icons.feedback),
            onPressed: () => _showFeedbackDialog(context),
            tooltip: 'Provide Feedback',
          ),
          IconButton(
            icon: const Icon(Icons.chat),
            onPressed: () {
              context.push('/documents/${widget.jobId}/chat');
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_result?['summary'] != null) ...[
              Text('Summary', style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(_result!['summary'] as String),
                ),
              ),
              const SizedBox(height: 24),
            ],
            if (_result?['entities'] != null) ...[
              Text(
                'Extracted Entities',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              ...((_result!['entities'] as Map<String, dynamic>?)?['entities']
                          as List<dynamic>? ??
                      [])
                  .map(
                    (entity) => Card(
                      child: ListTile(
                        title: Text(entity['text'] as String? ?? ''),
                        subtitle: Text(entity['type'] as String? ?? ''),
                      ),
                    ),
                  )
                  .toList(),
              const SizedBox(height: 24),
            ],
            if (_result?['ocr_text'] != null) ...[
              Text(
                'Extracted Text',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    (_result!['ocr_text'] as String? ?? '').substring(
                          0,
                          ((_result!['ocr_text'] as String?)?.length ?? 0) > 500
                              ? 500
                              : (_result!['ocr_text'] as String?)?.length ?? 0,
                        ) +
                        '...',
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
