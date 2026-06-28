import 'package:shared_preferences/shared_preferences.dart';

class ConfigService {
  static const String _serverUrlKey = 'server_url';
  String _serverUrl = '';
  SharedPreferences? _prefs;

  String get serverUrl => _serverUrl;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _serverUrl = _prefs?.getString(_serverUrlKey) ?? '';
  }

  Future<void> setServerUrl(String url) async {
    _serverUrl = url;
    await _prefs?.setString(_serverUrlKey, url);
  }

  Future<void> clearConfig() async {
    _serverUrl = '';
    await _prefs?.remove(_serverUrlKey);
  }
}