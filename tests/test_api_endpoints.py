import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_hyperliquid_service():
    """Mock HyperliquidService for testing."""
    with patch('app.api.routers.root.hs') as mock:
        mock.exchange_instance = MagicMock()
        mock.account_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        yield mock


@pytest.fixture
def client(mock_hyperliquid_service):
    """Create test client."""
    from app.api.app import create_app
    app = create_app()
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns correct message."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Hyperliquid API running"}


def test_health_endpoint_configured(client, mock_hyperliquid_service):
    """Test health endpoint when exchange is configured."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["service"] == "hyperliquid-api"
    assert data["exchange_configured"] is True
    assert "account_address" in data


def test_health_endpoint_not_configured(client):
    """Test health endpoint when exchange not configured."""
    with patch('app.api.routers.root.hs') as mock_hs:
        mock_hs.exchange_instance = None
        mock_hs.account_address = None
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert data["exchange_configured"] is False


@patch('app.api.routers.v1.endpoints.trading.hs')
def test_create_market_order_success(mock_hs, client):
    """Test successful market order creation."""
    # Mock successful order
    mock_hs.create_market_order.return_value = {
        "status": "ok",
        "response": {
            "data": {
                "statuses": [{
                    "filled": {
                        "oid": 12345,
                        "totalSz": "0.1",
                        "avgPx": "50000"
                    }
                }]
            }
        }
    }
    
    response = client.post("/v1/order/market", json={
        "coin": "BTC",
        "is_buy": True,
        "size": 0.1,
        "slippage": 0.01
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert len(data["filled_orders"]) == 1
    assert data["filled_orders"][0]["oid"] == 12345
    assert data["filled_orders"][0]["totalSz"] == "0.1"
    assert data["errors"] == []


@patch('app.api.routers.v1.endpoints.trading.hs')
def test_create_market_order_exchange_not_configured(mock_hs, client):
    """Test market order when exchange not configured."""
    from app.core.exceptions import ExchangeNotConfiguredError
    mock_hs.create_market_order.side_effect = ExchangeNotConfiguredError()
    
    response = client.post("/v1/order/market", json={
        "coin": "BTC",
        "is_buy": True,
        "size": 0.1
    })
    
    assert response.status_code == 503
    assert "Exchange" in response.json()["detail"]


@patch('app.api.routers.v1.endpoints.trading.hs')
def test_create_market_order_trading_error(mock_hs, client):
    """Test market order with trading error."""
    from app.core.exceptions import TradingError
    mock_hs.create_market_order.side_effect = TradingError("ouverture", "Insufficient balance")
    
    response = client.post("/v1/order/market", json={
        "coin": "BTC",
        "is_buy": True,
        "size": 0.1
    })
    
    assert response.status_code == 500
    assert "ouverture" in response.json()["detail"]


@patch('app.api.routers.v1.endpoints.user_state.hs')
def test_get_user_state_success(mock_hs, client):
    """Test successful user state retrieval."""
    mock_hs.get_user_state.return_value = {
        'marginSummary': {
            'accountValue': '1000.50',
            'totalRawUsd': '1000.50'
        },
        'assetPositions': [
            {'position': {'coin': 'BTC', 'szi': '0.1'}}
        ]
    }
    
    response = client.get("/v1/user/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["accountValue"] == "1000.50"
    assert data["numPositions"] == 1


@patch('app.api.routers.v1.endpoints.user_state.hs')
def test_get_user_state_not_found(mock_hs, client):
    """Test user state when address not found."""
    mock_hs.get_user_state.return_value = None
    
    response = client.get("/v1/user/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    
    assert response.status_code == 404
