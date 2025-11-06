import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/storage_service.dart';
import '../../../routing/app_router.dart';
import 'document_result_screen.dart';
import 'package:go_router/go_router.dart';

class DocumentListScreen extends ConsumerStatefulWidget {
  const DocumentListScreen({super.key});

  @override
  ConsumerState<DocumentListScreen> createState() => _DocumentListScreenState();
}

class _DocumentListScreenState extends ConsumerState<DocumentListScreen> {
  List<Map<String, dynamic>> _jobs = [];
  bool _isLoading = true;
  String? _searchQuery;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final storageService = StorageService();
      final jobs = await storageService.getJobs();
      setState(() {
        _jobs = jobs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error loading documents: $e')));
      }
    }
  }

  List<Map<String, dynamic>> get _filteredJobs {
    if (_searchQuery == null || _searchQuery!.isEmpty) {
      return _jobs;
    }
    return _jobs.where((job) {
      final filename = (job['filename'] as String? ?? '').toLowerCase();
      return filename.contains(_searchQuery!.toLowerCase());
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search documents...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredJobs.isEmpty
                ? const Center(child: Text('No documents found'))
                : RefreshIndicator(
                    onRefresh: _loadJobs,
                    child: ListView.builder(
                      itemCount: _filteredJobs.length,
                      itemBuilder: (context, index) {
                        final job = _filteredJobs[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          child: ListTile(
                            leading: const Icon(Icons.description),
                            title: Text(
                              job['filename'] as String? ?? 'Unknown',
                            ),
                            subtitle: Text(
                              'Status: ${job['status'] ?? 'Unknown'}',
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                if (job['status'] == 'completed')
                                  IconButton(
                                    icon: const Icon(Icons.chat),
                                    onPressed: () {
                                      context.push(
                                        '/documents/${job['job_id']}/chat',
                                      );
                                    },
                                  ),
                                PopupMenuButton(
                                  itemBuilder: (context) => [
                                    const PopupMenuItem(
                                      value: 'view',
                                      child: Text('View'),
                                    ),
                                    const PopupMenuItem(
                                      value: 'share',
                                      child: Text('Share'),
                                    ),
                                    const PopupMenuItem(
                                      value: 'delete',
                                      child: Text('Delete'),
                                    ),
                                  ],
                                  onSelected: (value) {
                                    if (value == 'view') {
                                      context.push(
                                        '/documents/${job['job_id']}',
                                      );
                                    } else if (value == 'delete') {
                                      _deleteJob(job['job_id'] as String);
                                    }
                                  },
                                ),
                              ],
                            ),
                            onTap: () {
                              context.push('/documents/${job['job_id']}');
                            },
                          ),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/capture'),
        icon: const Icon(Icons.camera_alt),
        label: const Text('Capture Document'),
      ),
    );
  }

  Future<void> _deleteJob(String jobId) async {
    try {
      final storageService = StorageService();
      await storageService.deleteJob(jobId);
      await _loadJobs();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Document deleted')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error deleting document: $e')));
      }
    }
  }
}
