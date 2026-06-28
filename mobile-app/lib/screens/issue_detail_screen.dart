import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'dart:io';
import '../services/api_service.dart';
import '../models/safety_issue.dart';

class IssueDetailScreen extends StatefulWidget {
  final int issueId;

  const IssueDetailScreen({Key? key, required this.issueId}) : super(key: key);

  @override
  State<IssueDetailScreen> createState() => _IssueDetailScreenState();
}

class _IssueDetailScreenState extends State<IssueDetailScreen> {
  SafetyIssue? _issue;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadIssue();
  }

  Future<void> _loadIssue() async {
    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final issue = await apiService.getIssue(widget.issueId);

      setState(() {
        _issue = issue;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载失败: $e')),
      );
    }
  }

  Future<void> _uploadRectificationPhoto() async {
    final picker = ImagePicker();
    final XFile? photo = await picker.pickImage(source: ImageSource.camera);

    if (photo != null && _issue != null) {
      try {
        final apiService = context.read<ApiService>();
        await apiService.uploadPhoto(
          issueId: _issue!.id,
          photoType: '整改照片',
          photos: [File(photo.path)],
        );

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('整改照片已上传')),
        );

        _loadIssue();
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('上传失败: $e')),
        );
      }
    }
  }

  Future<void> _updateStatus(String status) async {
    if (_issue == null) return;

    try {
      final apiService = context.read<ApiService>();
      await apiService.updateStatus(_issue!.id, status);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('状态已更新')),
      );

      _loadIssue();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('更新失败: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('问题详情')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _issue == null
              ? const Center(child: Text('问题不存在'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        _issue!.title,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      Text('位置: ${_issue!.location ?? '未知'}'),
                      Text('严重程度: ${_issue!.severity}'),
                      Text('责任人: ${_issue!.responsiblePerson ?? '未指定'}'),
                      const SizedBox(height: 16),
                      const Text('问题描述:', style: TextStyle(fontSize: 16)),
                      Text(_issue!.description ?? '无'),
                      const SizedBox(height: 16),
                      DropdownButtonFormField<String>(
                        value: _issue!.status,
                        decoration: const InputDecoration(
                          labelText: '状态',
                          border: OutlineInputBorder(),
                        ),
                        items: ['待整改', '整改中', '已完成']
                            .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                            .toList(),
                        onChanged: (value) => _updateStatus(value ?? _issue!.status),
                      ),
                      const SizedBox(height: 24),
                      const Text('问题照片:', style: TextStyle(fontSize: 16)),
                      const SizedBox(height: 8),
                      if (_issue!.issuePhotos.isEmpty)
                        const Text('无问题照片')
                      else
                        SizedBox(
                          height: 100,
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: _issue!.issuePhotos.length,
                            itemBuilder: (context, index) {
                              final photo = _issue!.issuePhotos[index];
                              final apiService = context.read<ApiService>();
                              return Padding(
                                padding: const EdgeInsets.all(4.0),
                                child: CachedNetworkImage(
                                  imageUrl: apiService.getPhotoUrl(photo.id),
                                  width: 80,
                                  height: 80,
                                  fit: BoxFit.cover,
                                  placeholder: (context, url) =>
                                      const CircularProgressIndicator(),
                                  errorWidget: (context, url, error) =>
                                      const Icon(Icons.error),
                                ),
                              );
                            },
                          ),
                        ),
                      const SizedBox(height: 24),
                      const Text('整改照片:', style: TextStyle(fontSize: 16)),
                      const SizedBox(height: 8),
                      if (_issue!.rectificationPhotos.isEmpty)
                        const Text('无整改照片')
                      else
                        SizedBox(
                          height: 100,
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: _issue!.rectificationPhotos.length,
                            itemBuilder: (context, index) {
                              final photo = _issue!.rectificationPhotos[index];
                              final apiService = context.read<ApiService>();
                              return Padding(
                                padding: const EdgeInsets.all(4.0),
                                child: CachedNetworkImage(
                                  imageUrl: apiService.getPhotoUrl(photo.id),
                                  width: 80,
                                  height: 80,
                                  fit: BoxFit.cover,
                                  placeholder: (context, url) =>
                                      const CircularProgressIndicator(),
                                  errorWidget: (context, url, error) =>
                                      const Icon(Icons.error),
                                ),
                              );
                            },
                          ),
                        ),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _uploadRectificationPhoto,
                        icon: const Icon(Icons.camera_alt),
                        label: const Text('上传整改照片'),
                      ),
                    ],
                  ),
                ),
    );
  }
}