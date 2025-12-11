
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../services/timeline_provider.dart';

class PostUpdateScreen extends StatefulWidget {
  const PostUpdateScreen({super.key});

  @override
  State<PostUpdateScreen> createState() => _PostUpdateScreenState();
}

class _PostUpdateScreenState extends State<PostUpdateScreen> {
  final _textController = TextEditingController();
  final ImagePicker _picker = ImagePicker();

  bool _isUploading = false;
  XFile? _selectedImage;

  Future<void> _pickImage() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _selectedImage = image;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error picking image: $e')),
        );
      }
    }
  }

  Future<void> _submit() async {
    if (_textController.text.isEmpty && _selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter text or select an image')),
      );
      return;
    }

    setState(() {
      _isUploading = true;
    });

    try {
      final provider = context.read<TimelineProvider>();

      if (_selectedImage != null) {
         final bytes = await _selectedImage!.readAsBytes();
         await provider.addImage(
           _textController.text,
           bytes,
           _selectedImage!.name
         );
      } else {
        await provider.addStatusUpdate(_textController.text);
      }

      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Update'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _textController,
              decoration: const InputDecoration(
                labelText: 'How are you feeling?',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),

            if (_selectedImage != null) ...[
              Stack(
                alignment: Alignment.topRight,
                children: [
                  Container(
                    height: 150,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: kIsWeb
                        ? Image.network(_selectedImage!.path, fit: BoxFit.cover)
                        : Image.file(File(_selectedImage!.path), fit: BoxFit.cover),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.red),
                    onPressed: () {
                      setState(() {
                        _selectedImage = null;
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 16),
            ] else
              OutlinedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.image),
                label: const Text('Add Image'),
              ),

            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _isUploading ? null : _submit,
                child: _isUploading
                  ? const CircularProgressIndicator()
                  : const Text('Post'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
