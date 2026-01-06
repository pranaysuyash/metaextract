# Batch extraction test fix

Old code had bug:

```python
for i, img_path in enumerate(self.test_images[:3]):
    with open(img_path, 'rb') as f:  # Files closed after loop
        files.append(('files', (f'test_{i}.jpg', f, 'image/jpeg')))

response = requests.post(...)  # Files already closed! ERROR: "read of closed file"
```

Fixed code:

```python
files = []
for i, img_path in enumerate(self.test_images[:3]):
    with open(img_path, 'rb') as f:
        file_content = f.read()
    files.append(('files', (f'test_{i}.jpg', io.BytesIO(file_content), 'image/jpeg')))

response = requests.post(...)  # Works because BytesIO is in memory
```

This fix applies to both:

- Batch extraction test (line 209-245)
- Timeline reconstruction test (line 267-294)
