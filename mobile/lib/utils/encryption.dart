import 'dart:convert';
import 'dart:typed_data';
import 'package:cryptography/cryptography.dart';

class EncryptionUtil {
  static Future<SecretKey> _getKey(String password) async {
    final salt = utf8.encode('analyzer_salt_2024');
    final pbkdf2 = Pbkdf2(
      macAlgorithm: Hmac.sha256(),
      iterations: 100000,
      bits: 256,
    );
    return await pbkdf2.deriveKeyFromPassword(password: password, nonce: salt);
  }

  static Future<Uint8List> encryptFile(Uint8List data, String password) async {
    final key = await _getKey(password);
    final algorithm = AesGcm.with256bits();
    final secretBox = await algorithm.encrypt(data, secretKey: key);
    return secretBox.concatenation();
  }

  static Future<Uint8List> decryptFile(
    Uint8List encryptedData,
    String password,
  ) async {
    final key = await _getKey(password);
    final algorithm = AesGcm.with256bits();
    final secretBox = SecretBox.fromConcatenation(
      encryptedData,
      nonceLength: 12,
      macLength: 16,
    );
    final decrypted = await algorithm.decrypt(secretBox, secretKey: key);
    return Uint8List.fromList(decrypted);
  }
}
