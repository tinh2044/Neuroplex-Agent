# Backend API Test Suite

Đây là test suite hoàn chỉnh cho backend API của Neuroplex.

## 📁 Cấu Trúc Test

```
tests/
├── __init__.py                 # Test package init
├── conftest.py                 # Pytest fixtures và configuration
├── test_base_routes.py         # Test cho base routes (/base)
├── test_chat_routes.py         # Test cho chat routes (/chat)
├── test_data_routes.py         # Test cho data routes (/data)
├── test_tool_routes.py         # Test cho tool routes (/tool)
├── test_admin_routes.py        # Test cho admin routes (/admin)
└── README.md                   # Tài liệu này
```

## 🚀 Chạy Tests

### Cài đặt dependencies
```bash
pip install -r requirements-test.txt
```

### Chạy tất cả tests
```bash
pytest
```

### Chạy tests cho một module cụ thể
```bash
pytest tests/test_admin_routes.py
pytest tests/test_chat_routes.py
pytest tests/test_data_routes.py
```

### Chạy với coverage report
```bash
pytest --cov=backend --cov-report=html
```

### Chạy tests song song (nhanh hơn)
```bash
pytest -n auto
```

## 🧪 Loại Tests

### 1. Unit Tests
- Test các function/method riêng lẻ
- Mock tất cả dependencies
- Chạy nhanh, isolated

### 2. Integration Tests
- Test tương tác giữa các components
- Test với database thật (test DB)
- Test API endpoints end-to-end

### 3. Error Handling Tests
- Test các trường hợp lỗi
- Test validation
- Test exception handling

## 📊 Test Coverage

Targets:
- **Overall coverage**: >= 80%
- **Critical routes coverage**: >= 90%
- **Error handling coverage**: >= 70%

Xem coverage report:
```bash
# Terminal report
pytest --cov=backend --cov-report=term-missing

# HTML report
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## 🔧 Test Configuration

### Fixtures (conftest.py)
- `client`: FastAPI test client với mocked dependencies
- `db_session`: Test database session
- `sample_token_data`: Sample data cho token tests
- `sample_chat_data`: Sample data cho chat tests
- `mock_ai_components`: Mock AI engine components

### Mocking Strategy
- **AI Engine**: Hoàn toàn mock để tránh dependencies
- **Database**: Sử dụng SQLite in-memory cho tests
- **File Operations**: Mock file I/O operations
- **External APIs**: Mock tất cả external calls

## 📝 Viết Tests Mới

### Naming Convention
```python
def test_function_name_scenario():
    """Test description"""
    # Arrange
    # Act  
    # Assert
```

### Test Classes
```python
class TestFeatureName:
    """Test class cho feature cụ thể"""
    
    def test_happy_path(self, client):
        """Test trường hợp thành công"""
        pass
        
    def test_error_case(self, client):
        """Test trường hợp lỗi"""
        pass
```

### Assertions Best Practices
```python
# Good
assert response.status_code == 200
assert "expected_key" in response.json()
assert response.json()["key"] == "expected_value"

# Comprehensive API testing
response = client.post("/endpoint", json=data)
assert response.status_code == 200
result = response.json()
assert result["status"] == "success"
assert "data" in result
```

## 🎯 Test Scenarios Covered

### Base Routes (/base)
- ✅ Configuration management
- ✅ Service restart
- ✅ Log retrieval
- ✅ Error handling

### Admin Routes (/admin)
- ✅ Token CRUD operations
- ✅ Token verification
- ✅ Database operations
- ✅ Full lifecycle testing

### Chat Routes (/chat)
- ✅ Simple chat calls
- ✅ Streaming responses
- ✅ Agent interactions
- ✅ Model management
- ✅ Error scenarios

### Data Routes (/data)
- ✅ Database management
- ✅ File operations
- ✅ Upload functionality
- ✅ Knowledge graph operations
- ✅ Query testing

### Tool Routes (/tool)
- ✅ Tool listing
- ✅ Text chunking
- ✅ PDF processing
- ✅ Agent integration

## 🐛 Debug Tests

### Verbose output
```bash
pytest -v -s
```

### Stop on first failure
```bash
pytest -x
```

### Run specific test
```bash
pytest tests/test_admin_routes.py::TestAdminTokenRoutes::test_create_token
```

### Debug với pdb
```python
def test_something():
    import pdb; pdb.set_trace()
    # Your test code
```

## 🔄 CI/CD Integration

Test suite được thiết kế để chạy trong CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=backend --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## 📈 Performance Testing

Để test performance:
```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run performance tests
pytest --benchmark-only
```

## 🤝 Contributing

Khi thêm feature mới:
1. Viết tests trước (TDD)
2. Đảm bảo coverage >= 80%
3. Test cả happy path và error cases
4. Update documentation nếu cần

## 🆘 Troubleshooting

### Common Issues

1. **Import errors**: Đảm bảo `PYTHONPATH` correct
2. **Database errors**: Check test database permissions
3. **Mocking issues**: Verify mock paths are correct
4. **Async issues**: Use `pytest-asyncio` for async tests

### Getting Help

- Check test logs với `pytest -v -s`
- Review mock configurations trong `conftest.py`
- Kiểm tra dependencies trong `requirements-test.txt` 