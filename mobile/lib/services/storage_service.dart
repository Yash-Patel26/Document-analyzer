import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../core/constants.dart';

class StorageService {
  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, AppConstants.databaseName);

    return await openDatabase(
      path,
      version: AppConstants.databaseVersion,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Jobs table
    await db.execute('''
      CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        status TEXT NOT NULL,
        progress REAL DEFAULT 0.0,
        created_at INTEGER NOT NULL,
        updated_at INTEGER,
        completed_at INTEGER
      )
    ''');

    // Upload queue table
    await db.execute('''
      CREATE TABLE upload_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        filename TEXT NOT NULL,
        status TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL,
        updated_at INTEGER
      )
    ''');

    // Chat messages table
    await db.execute('''
      CREATE TABLE chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        user_message TEXT NOT NULL,
        assistant_message TEXT,
        created_at INTEGER NOT NULL
      )
    ''');
  }

  // Job operations
  Future<int> insertJob(Map<String, dynamic> job) async {
    final db = await database;
    return await db.insert('jobs', job);
  }

  Future<List<Map<String, dynamic>>> getJobs() async {
    final db = await database;
    return await db.query('jobs', orderBy: 'created_at DESC');
  }

  Future<Map<String, dynamic>?> getJob(String jobId) async {
    final db = await database;
    final results = await db.query(
      'jobs',
      where: 'job_id = ?',
      whereArgs: [jobId],
      limit: 1,
    );
    return results.isEmpty ? null : results.first;
  }

  Future<int> updateJob(String jobId, Map<String, dynamic> updates) async {
    final db = await database;
    return await db.update(
      'jobs',
      updates,
      where: 'job_id = ?',
      whereArgs: [jobId],
    );
  }

  Future<int> deleteJob(String jobId) async {
    final db = await database;
    return await db.delete(
      'jobs',
      where: 'job_id = ?',
      whereArgs: [jobId],
    );
  }

  // Upload queue operations
  Future<int> addToUploadQueue(Map<String, dynamic> item) async {
    final db = await database;
    return await db.insert('upload_queue', item);
  }

  Future<List<Map<String, dynamic>>> getUploadQueue() async {
    final db = await database;
    return await db.query(
      'upload_queue',
      where: 'status = ?',
      whereArgs: ['pending'],
      orderBy: 'created_at ASC',
    );
  }

  Future<int> updateUploadQueueItem(int id, Map<String, dynamic> updates) async {
    final db = await database;
    return await db.update(
      'upload_queue',
      updates,
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}

