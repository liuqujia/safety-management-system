import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../services/api_service.dart';
import '../services/config_service.dart';
import '../models/safety_issue.dart';
import 'add_issue_screen.dart';
import 'issue_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<SafetyIssue> _issues = [];
  String _statusFilter = '';
  String _severityFilter = '';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadIssues();
  }

  Future<void> _loadIssues() async {
    setState(() => _isLoading = true);

    try {
      final apiService = context.read<ApiService>();
      final issues = await apiService.getIssues(
        status: _statusFilter,
        severity: _severityFilter,
      );

      setState(() {
        _issues = issues;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载失败: $e')),
      );
    }
  }

  Future<void> _takePhotoAndAddIssue() async {
    final picker = ImagePicker();
    final XFile? photo = await picker.pickImage(source: ImageSource.camera);

    if (photo != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => AddIssueScreen(photos: [File(photo.path)]),
        ),
      ).then((_) => _loadIssues());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('安全整改管理'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.pushNamed(context, '/config').then((_) => _loadIssues());
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 筛选器
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: DropdownButton<String>(
                    value: _statusFilter.isEmpty ? null : _statusFilter,
                    hint: const Text('状态筛选'),
                    items: ['待整改', '整改中', '已完成']
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (value) {
                      setState(() => _statusFilter = value ?? '');
                      _loadIssues();
                    },
                  ),
                ),
                Expanded(
                  child: DropdownButton<String>(
                    value: _severityFilter.isEmpty ? null : _severityFilter,
                    hint: const Text('严重程度'),
                    items: ['轻微', '一般', '严重']
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (value) {
                      setState(() => _severityFilter = value ?? '');
                      _loadIssues();
                    },
                  ),
                ),
              ],
            ),
          ),

          // 问题列表
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _issues.isEmpty
                    ? const Center(child: Text('暂无问题记录'))
                    : ListView.builder(
                        itemCount: _issues.length,
                        itemBuilder: (context, index) {
                          final issue = _issues[index];
                          return Card(
                            child: ListTile(
                              title: Text(issue.title),
                              subtitle: Text('${issue.location ?? ''} - ${issue.status}'),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    _getSeverityIcon(issue.severity),
                                    color: _getSeverityColor(issue.severity),
                                  ),
                                  Text('${issue.photoCount}张'),
                                ],
                              ),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        IssueDetailScreen(issueId: issue.id),
                                  ),
                                ).then((_) => _loadIssues());
                              },
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _takePhotoAndAddIssue,
        child: const Icon(Icons.camera_alt),
        tooltip: '拍照记录问题',
      ),
    );
  }

  IconData _getSeverityIcon(String severity) {
    switch (severity) {
      case '轻微':
        return Icons.info_outline;
      case '一般':
        return Icons.warning;
      case '严重':
        return Icons.error;
      default:
        return Icons.info_outline;
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity) {
      case '轻微':
        return Colors.blue;
      case '一般':
        return Colors.orange;
      case '严重':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}