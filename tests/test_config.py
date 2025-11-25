from eth_utils import is_address, to_checksum_address


def test_valid_ethereum_address_validation():
    """Test that eth-utils correctly validates Ethereum addresses."""
    valid_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    assert is_address(valid_address)
    
    invalid_address = "0xinvalid"
    assert not is_address(invalid_address)


def test_checksum_conversion():
    """Test that addresses are converted to checksum format."""
    lowercase = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    checksum = to_checksum_address(lowercase)
    # Checksum version should be different from lowercase
    assert checksum != lowercase
    assert is_address(checksum)
    

def test_import_exceptions():
    """Test that custom exceptions can be imported."""
    from app.core.exceptions import (
        InvalidAddressError,
        ConfigurationError,
        ExchangeNotConfiguredError
    )
    
    error1 = InvalidAddressError("0xtest", "invalid")
    assert "0xtest" in str(error1)
    
    error2 = ConfigurationError("KEY", "reason")  
    assert "KEY" in str(error2)
    
    error3 = ExchangeNotConfiguredError()
    assert "Exchange" in str(error3)
