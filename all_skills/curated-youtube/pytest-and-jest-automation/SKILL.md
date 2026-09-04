---
name: pytest-and-jest-automation
description: "Automated testing with Python pytest, fixtures, parameterization, mocks, and code coverage. Use when generating unit and integration tests for Python backends, mocking external dependencies, or analyzing test suites."
risk: safe
source: curated-youtube
---
# Automação de Testes com Pytest

## When to Use
- Criar suítes de testes unitários ou de integração para serviços e utilitários em Python.
- Configurar fixtures com escopos adequados (`function`, `module`, `session`).
- Testar múltiplos cenários usando `@pytest.mark.parametrize` e mocks assíncronos.
- Medir cobertura de código via `pytest-cov`.

## Padrões Essenciais de Código

### 1. Fixtures e Injeção de Dependência
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def api_client():
    client = MagicMock()
    client.get.return_value = {"status": "ok", "data": [1, 2, 3]}
    return client

def test_fetch_data(api_client):
    result = api_client.get("/endpoint")
    assert result["status"] == "ok"
    assert len(result["data"]) == 3
```

### 2. Parametrização de Cenários
```python
import pytest

def calculate_discount(price: float, percentage: float) -> float:
    if percentage < 0 or percentage > 100:
        raise ValueError("Invalid percentage")
    return price * (1 - percentage / 100)

@pytest.mark.parametrize("price, percentage, expected", [
    (100.0, 10.0, 90.0),
    (50.0, 0.0, 50.0),
    (200.0, 50.0, 100.0),
])
def test_calculate_discount_success(price, percentage, expected):
    assert calculate_discount(price, percentage) == pytest.approx(expected)

def test_calculate_discount_invalid():
    with pytest.raises(ValueError, match="Invalid percentage"):
        calculate_discount(100.0, -5.0)
```

### 3. Comandos de Execução
```bash
# Execução padrão com saída verbosa
pytest -v

# Executar arquivo específico com cobertura
pytest tests/test_services.py --cov=app --cov-report=term-missing

# Executar testes marcados
pytest -m "not slow" -k "test_calculate"
```
