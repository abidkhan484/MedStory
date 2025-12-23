
class User {
  final int id;
  final String email;
  final String fullName;
  final bool isVerified;
  final String? accessToken;
  final String? refreshToken;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.isVerified,
    this.accessToken,
    this.refreshToken,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      email: json['email'] as String,
      fullName: json['full_name'] as String,
      isVerified: json['is_verified'] as bool,
    );
  }
}

class AuthToken {
  final String accessToken;
  final String refreshToken;

  AuthToken({required this.accessToken, required this.refreshToken});

  factory AuthToken.fromJson(Map<String, dynamic> json) {
    return AuthToken(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
    );
  }
}
