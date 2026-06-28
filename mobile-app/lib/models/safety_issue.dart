class SafetyIssue {
  final int id;
  final String title;
  final String? description;
  final String? location;
  final String severity;
  final String status;
  final String? responsiblePerson;
  final String? deadline;
  final String? notes;
  final String? createTime;
  final String? updateTime;
  final int photoCount;
  final List<Photo> issuePhotos;
  final List<Photo> rectificationPhotos;

  SafetyIssue({
    required this.id,
    required this.title,
    this.description,
    this.location,
    required this.severity,
    required this.status,
    this.responsiblePerson,
    this.deadline,
    this.notes,
    this.createTime,
    this.updateTime,
    this.photoCount = 0,
    this.issuePhotos = [],
    this.rectificationPhotos = [],
  });

  factory SafetyIssue.fromJson(Map<String, dynamic> json) {
    return SafetyIssue(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      location: json['location'],
      severity: json['severity'],
      status: json['status'],
      responsiblePerson: json['responsible_person'],
      deadline: json['deadline'],
      notes: json['notes'],
      createTime: json['create_time'],
      updateTime: json['update_time'],
      photoCount: json['photo_count'] ?? 0,
      issuePhotos: (json['issue_photos'] as List?)
              ?.map((p) => Photo.fromJson(p))
              .toList() ?? [],
      rectificationPhotos: (json['rectification_photos'] as List?)
              ?.map((p) => Photo.fromJson(p))
              .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'location': location,
      'severity': severity,
      'status': status,
      'responsible_person': responsiblePerson,
      'deadline': deadline,
      'notes': notes,
      'create_time': createTime,
      'update_time': updateTime,
      'photo_count': photoCount,
    };
  }
}

class Photo {
  final int id;
  final int issueId;
  final String photoType;
  final String fileName;
  final String? uploadTime;
  final String? description;
  final String url;

  Photo({
    required this.id,
    required this.issueId,
    required this.photoType,
    required this.fileName,
    this.uploadTime,
    this.description,
    required this.url,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      id: json['id'],
      issueId: json['issue_id'],
      photoType: json['photo_type'],
      fileName: json['file_name'],
      uploadTime: json['upload_time'],
      description: json['description'],
      url: json['url'],
    );
  }
}