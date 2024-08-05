import pytest
from unittest.mock import patch,Mock
from app.controllers.main_controller import MainController
from werkzeug.datastructures import FileStorage
from io import BytesIO
from app import create_app

@pytest.fixture
def app():
        app = create_app()
        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test_secret_key',
            'SERVER_NAME': 'localhost:8000'
        })
        return app

@pytest.fixture
def client(app):
    return app.test_client()

""" @pytest.fixture
    def main_controller(self):
        with patch('app.controllers.main_controller.logger') as mock_logger:
            return MainController()
"""
@pytest.fixture
def main_controller(app):
    with app.app_context():
        with patch('app.controllers.main_controller.logger') as mock_logger:
            return MainController()



class TestMainController:

   
    def test_initialization(self, main_controller):
        """Test the initialization of MainController."""
        assert main_controller.template_name == "welcome.html"
        assert main_controller.title == "Welcome - Inventory Data Hub"

    def test_render(self, main_controller):
        """Test the rendering functionality of MainController."""
        with patch('app.controllers.main_controller.render_template') as mock_render_template:
            # Mocking render_template to return a predefined value
            mock_render_template.return_value = "Rendered Template"
            result = main_controller.render()
            mock_render_template.assert_called_once_with('welcome.html', title='Welcome - Inventory Data Hub')

    def test_validate_files_nfmp2_valid(self, main_controller):
        """Test file validation for NFMP2 with valid files."""
        # Create simulated files for NFMP2
        
        
  
        nfmp2_files = [
            FileStorage(stream=BytesIO(b"dummy content"), filename=f'{cat}_01012023_NFMP1.csv') for cat in [
            'cards', 'flash_memory', 'media_adaptor', 'power_supply', 'shelf', 'network_element', 'port', 'port_connector'
            ]
        ] + [
            FileStorage(stream=BytesIO(b"dummy content"), filename=f'{cat}_01012023_NFMP2.csv') for cat in [
            'cards', 'flash_memory', 'media_adaptor', 'power_supply', 'shelf', 'network_element', 'port', 'port_connector'
            ]
        ]

        # Test NFMP2 validation
        valid, temp_files, error_message = main_controller.validate_files_two_nfmp(nfmp2_files)

        assert valid == True
        assert temp_files != []
        assert error_message == ""

    def test_validate_files_nfmp2_invalid(self, main_controller):
        """Test file validation for NFMP2 with invalid files."""
        # Create simulated invalid files for NFMP2
        invalid_files = [
            FileStorage(stream=BytesIO(b"dummy content"), filename='invalid_file.txt')  # Invalid file
        ]

        # Test NFMP2 validation with invalid files
        valid, temp_files, error_message = main_controller.validate_files_two_nfmp(invalid_files)
        assert valid == False
        assert temp_files == []
        assert error_message != ""

   