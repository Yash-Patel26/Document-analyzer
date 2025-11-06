import 'dart:io';
import 'package:workmanager/workmanager.dart';
import '../services/document_service.dart';
import '../services/storage_service.dart';
import '../core/constants.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'api_client.dart';

class UploadService {
  final DocumentService _documentService;
  final StorageService _storageService;
  final Connectivity _connectivity = Connectivity();

  UploadService(this._documentService, this._storageService);

  Future<void> uploadDocument(File file) async {
    // Check connectivity
    final connectivityResult = await _connectivity.checkConnectivity();
    if (connectivityResult == ConnectivityResult.none) {
      // Add to queue for later
      await _storageService.addToUploadQueue({
        'file_path': file.path,
        'filename': file.path.split('/').last,
        'status': 'pending',
        'retry_count': 0,
        'created_at': DateTime.now().millisecondsSinceEpoch,
      });
      return;
    }

    try {
      final result = await _documentService.uploadDocument(file);
      final jobId = result['job_id'] as String;

      // Save job to local storage
      await _storageService.insertJob({
        'job_id': jobId,
        'filename': file.path.split('/').last,
        'file_path': file.path,
        'status': 'pending',
        'progress': 0.0,
        'created_at': DateTime.now().millisecondsSinceEpoch,
      });

      // Trigger analysis
      await _documentService.triggerAnalysis(jobId);
    } catch (e) {
      // Add to queue on error
      await _storageService.addToUploadQueue({
        'file_path': file.path,
        'filename': file.path.split('/').last,
        'status': 'pending',
        'retry_count': 0,
        'created_at': DateTime.now().millisecondsSinceEpoch,
      });
      rethrow;
    }
  }

  Future<void> processUploadQueue() async {
    final queue = await _storageService.getUploadQueue();

    for (var item in queue) {
      final file = File(item['file_path'] as String);
      if (await file.exists()) {
        try {
          await uploadDocument(file);
          // Mark as completed
          await _storageService.updateUploadQueueItem(item['id'] as int, {
            'status': 'completed',
          });
        } catch (e) {
          // Increment retry count
          final retryCount = (item['retry_count'] as int) + 1;
          if (retryCount < AppConstants.maxRetries) {
            await _storageService.updateUploadQueueItem(item['id'] as int, {
              'retry_count': retryCount,
              'updated_at': DateTime.now().millisecondsSinceEpoch,
            });
          } else {
            // Mark as failed
            await _storageService.updateUploadQueueItem(item['id'] as int, {
              'status': 'failed',
            });
          }
        }
      }
    }
  }

  static void callbackDispatcher() {
    Workmanager().executeTask((task, inputData) async {
      // Initialize services
      final storageService = StorageService();
      final documentService = DocumentService(ApiClient());
      final uploadService = UploadService(documentService, storageService);

      await uploadService.processUploadQueue();
      return Future.value(true);
    });
  }
}
