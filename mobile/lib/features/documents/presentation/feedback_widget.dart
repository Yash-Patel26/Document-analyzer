import 'package:flutter/material.dart';

class FeedbackWidget extends StatefulWidget {
  final String jobId;
  final String type; // 'summary', 'entity', 'qa'
  final Function(Map<String, dynamic>) onFeedbackSubmitted;

  const FeedbackWidget({
    super.key,
    required this.jobId,
    required this.type,
    required this.onFeedbackSubmitted,
  });

  @override
  State<FeedbackWidget> createState() => _FeedbackWidgetState();
}

class _FeedbackWidgetState extends State<FeedbackWidget> {
  int _rating = 0;
  final TextEditingController _correctionController = TextEditingController();
  bool _isCorrect = true;

  @override
  void dispose() {
    _correctionController.dispose();
    super.dispose();
  }

  void _submitFeedback() {
    final feedback = {
      'job_id': widget.jobId,
      'type': widget.type,
      'rating': _rating,
      'is_correct': _isCorrect,
      'correction': _correctionController.text.trim().isNotEmpty
          ? _correctionController.text.trim()
          : null,
    };

    widget.onFeedbackSubmitted(feedback);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Provide Feedback - ${widget.type.toUpperCase()}'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Rate the quality (1-5):'),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(5, (index) {
                return IconButton(
                  icon: Icon(
                    index < _rating ? Icons.star : Icons.star_border,
                    color: Colors.amber,
                  ),
                  onPressed: () {
                    setState(() {
                      _rating = index + 1;
                    });
                  },
                );
              }),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: CheckboxListTile(
                    title: const Text('Is this correct?'),
                    value: _isCorrect,
                    onChanged: (value) {
                      setState(() {
                        _isCorrect = value ?? true;
                      });
                    },
                  ),
                ),
              ],
            ),
            if (!_isCorrect) ...[
              const SizedBox(height: 16),
              TextField(
                controller: _correctionController,
                decoration: const InputDecoration(
                  labelText: 'Provide correction',
                  hintText: 'Enter the correct version...',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(onPressed: _submitFeedback, child: const Text('Submit')),
      ],
    );
  }
}
