import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/documents/presentation/document_list_screen.dart';
import '../features/documents/presentation/document_capture_screen.dart';
import '../features/documents/presentation/document_result_screen.dart';
import '../features/documents/presentation/document_chat_screen.dart';
import '../features/settings/presentation/settings_screen.dart';
import '../providers/auth_provider.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: authState.isAuthenticated ? '/documents' : '/login',
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isLoggingIn = state.matchedLocation == '/login';

      if (!isAuthenticated && !isLoggingIn) {
        return '/login';
      }
      if (isAuthenticated && isLoggingIn) {
        return '/documents';
      }
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/documents',
        builder: (context, state) => const DocumentListScreen(),
      ),
      GoRoute(
        path: '/capture',
        builder: (context, state) => const DocumentCaptureScreen(),
      ),
      GoRoute(
        path: '/documents/:jobId',
        builder: (context, state) {
          final jobId = state.pathParameters['jobId']!;
          return DocumentResultScreen(jobId: jobId);
        },
      ),
      GoRoute(
        path: '/documents/:jobId/chat',
        builder: (context, state) {
          final jobId = state.pathParameters['jobId']!;
          return DocumentChatScreen(jobId: jobId);
        },
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});
