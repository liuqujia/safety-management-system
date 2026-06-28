import 'dart:io';
import 'package:dio/dio.dart';
import '../models/safety_issue.dart';

class ApiService {
  final Dio _dio;
  String baseUrl;

  ApiService({required this.baseUrl}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
    ));
  }

  void updateBaseUrl(String newUrl) {
    baseUrl = newUrl;
    _dio.options.baseUrl = newUrl;
  }

  // 获取问题列表
  Future<List<SafetyIssue>> getIssues({
    String? status,
    String? severity,
  }) async {
    try {
      final response = await _dio.get(
        '/api/issues/',
        queryParameters: {
          if (status != null) 'status': status,
          if (severity != null) 'severity': severity,
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => SafetyIssue.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      throw Exception('获取问题列表失败: $e');
    }
  }

  // 获取单个问题
  Future<SafetyIssue?> getIssue(int issueId) async {
    try {
      final response = await _dio.get('/api/issues/$issueId');

      if (response.statusCode == 200) {
        return SafetyIssue.fromJson(response.data);
      }
      return null;
    } catch (e) {
      throw Exception('获取问题详情失败: $e');
    }
  }

  // 创建问题（带照片）
  Future<SafetyIssue?> createIssue({
    required String title,
    String? description,
    String? location,
    String severity = '一般',
    String? responsiblePerson,
    String? deadline,
    String? notes,
    List<File>? photos,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'title': title,
        'description': description ?? '',
        'location': location ?? '',
        'severity': severity,
        'responsible_person': responsiblePerson ?? '',
        'deadline': deadline ?? '',
        'notes': notes ?? '',
      });

      if (photos != null && photos.isNotEmpty) {
        for (int i = 0; i < photos.length; i++) {
          formData.files.add(MapEntry(
            'photos',
            await MultipartFile.fromFile(
              photos[i].path,
              filename: photos[i].path.split('/').last,
            ),
          ));
        }
      }

      final response = await _dio.post(
        '/api/issues/with-photos',
        data: formData,
      );

      if (response.statusCode == 200) {
        return SafetyIssue.fromJson(response.data);
      }
      return null;
    } catch (e) {
      throw Exception('创建问题失败: $e');
    }
  }

  // 更新问题
  Future<SafetyIssue?> updateIssue(int issueId, Map<String, dynamic> data) async {
    try {
      final response = await _dio.put('/api/issues/$issueId', data: data);

      if (response.statusCode == 200) {
        return SafetyIssue.fromJson(response.data);
      }
      return null;
    } catch (e) {
      throw Exception('更新问题失败: $e');
    }
  }

  // 删除问题
  Future<bool> deleteIssue(int issueId) async {
    try {
      final response = await _dio.delete('/api/issues/$issueId');
      return response.statusCode == 200;
    } catch (e) {
      throw Exception('删除问题失败: $e');
    }
  }

  // 上传照片
  Future<SafetyIssue?> uploadPhoto({
    required int issueId,
    required String photoType,
    required List<File> photos,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'photo_type': photoType,
      });

      for (int i = 0; i < photos.length; i++) {
        formData.files.add(MapEntry(
          'photos',
          await MultipartFile.fromFile(
            photos[i].path,
            filename: photos[i].path.split('/').last,
          ),
        ));
      }

      final response = await _dio.post(
        '/api/issues/$issueId/photos',
        data: formData,
      );

      if (response.statusCode == 200) {
        return SafetyIssue.fromJson(response.data);
      }
      return null;
    } catch (e) {
      throw Exception('上传照片失败: $e');
    }
  }

  // 更新状态
  Future<SafetyIssue?> updateStatus(int issueId, String status) async {
    try {
      final response = await _dio.put(
        '/api/issues/$issueId/status',
        queryParameters: {'status': status},
      );

      if (response.statusCode == 200) {
        return SafetyIssue.fromJson(response.data);
      }
      return null;
    } catch (e) {
      throw Exception('更新状态失败: $e');
    }
  }

  // 获取照片URL
  String getPhotoUrl(int photoId) {
    return '$baseUrl/api/photos/$photoId/download';
  }
}