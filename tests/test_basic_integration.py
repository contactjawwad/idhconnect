import pytest
from app import create_app
from werkzeug.datastructures import FileStorage
from io import BytesIO

@pytest.fixture
def app():
    app=create_app()
    app.config.update({
        'TESTING':True,
        'SECRET_KEY' : 'test_secret_key',
        'SERVER_NAME' : 'localhost:8000'
    })
    return app

@pytest.fixture
def client(app):
    with app.app_context():
           yield app.test_client()

class TestBasicIntegration:
     def test_basic_workflow(self,client):
        response=client.get('/')
        assert response.status_code == 200
        assert 'Welcome - Inventory Data Hub' in response.get_data(as_text=True)

        # Testing valid NFMP2 file upload
        
        nfmp2_files = [
            FileStorage(stream=BytesIO(b"dummy content"), filename=f'{cat}_01012023_NFMP1.csv') for cat in [
            'cards', 'flash_memory', 'media_adaptor', 'power_supply', 'shelf', 'network_element', 'port', 'port_connector'
            ]
        ] + [
            FileStorage(stream=BytesIO(b"dummy content"), filename=f'{cat}_01012023_NFMP2.csv') for cat in [
            'cards', 'flash_memory', 'media_adaptor', 'power_supply', 'shelf', 'network_element', 'port', 'port_connector'
            ]
        ]


        valid_data = {
            'inventory_files': nfmp2_files
        }

        response = client.post('/validate', data=valid_data, content_type='multipart/form-data', headers={'NFMP-Mode': 'two_nfmp'})
        assert response.status_code == 200
        assert 'All files have been successfully uploaded' in response.get_data(as_text=True)

        with client.session_transaction() as sess:
            assert 'temp_files' in sess
            assert len(sess['temp_files']) == 16


          # Testing invalid file upload and error handling
        invalid_data = {
            'inventory_files': [
                (FileStorage(stream=BytesIO(b"invalid content"), filename='wrong_file_name.txt'), 'wrong_file_name.txt')
            ]
        }
        response = client.post('/validate', data=invalid_data, content_type='multipart/form-data', headers={'NFMP-Mode': 'two_nfmp'})
        assert response.status_code == 400  # Redirection to error page
        
        followup_response = client.get('/error')
        assert 'You selected the Wrong files Or Files are not in a supported format' in followup_response.get_data(as_text=True)

        assert followup_response.status_code == 200