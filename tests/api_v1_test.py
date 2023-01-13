from unittest.mock import patch
import pytest
from Flask_app.app import app


class TestAPI_v1:
    expected_json = b'{"CLS": {"lap_time": "1:12.829", "name": "Charles Leclerc", "org": "SAUBER FERRARI"}, ' \
                    b'"BHS": {"lap_time": "1:13.179", "name": "Brendon Hartley", "org": "SCUDERIA TORO ROSSO HONDA"}}'

    expected_xml = b"""<results>
  <CLS>
    <lap_time>1:12.829</lap_time>
    <name>Charles Leclerc</name>
    <org>SAUBER FERRARI</org>
  </CLS>
  <BHS>
    <lap_time>1:13.179</lap_time>
    <name>Brendon Hartley</name>
    <org>SCUDERIA TORO ROSSO HONDA</org>
  </BHS>
</results>"""

    expected_driver_json = b'{"lap_time": "1:12.829", "name": "Charles Leclerc", "org": "SAUBER FERRARI"}'
    expected_driver_xml = b"""<results>
  <lap_time>1:13.179</lap_time>
  <name>Brendon Hartley</name>
  <org>SCUDERIA TORO ROSSO HONDA</org>
</results>"""

    test_example = {
        "CLS": {
            "lap_time": "1:12.829",
            "name": "Charles Leclerc",
            "org": "SAUBER FERRARI"
        },
        "BHS": {
            "lap_time": "1:13.179",
            "name": "Brendon Hartley",
            "org": "SCUDERIA TORO ROSSO HONDA"
        }}

    @staticmethod
    @pytest.fixture()
    def client():
        client = app.test_client()
        return client

    @pytest.mark.parametrize('api_format, expected_res',
                             [
                                 ('json', expected_json),
                                 ('xml', expected_xml)
                             ])
    def test_api_v1(self, client, api_format, expected_res):
        with patch('Flask_app.views.api_endpoints.Report.build_report', return_value=self.test_example):
            return_value = client.get(f'http://127.0.0.1:5000/api/v1/report/?format={api_format}')

        assert return_value.status_code == 200
        assert return_value.data == expected_res

    @staticmethod
    @patch('Flask_app.views.api_endpoints.Report.build_report', return_value='None')
    def test_api_v1_error(patcher, client):
        return_value = client.get('http://127.0.0.1:5000/api/v1/report/?format=wrong_format')
        assert return_value.status_code == 400

    @pytest.mark.parametrize('api_format, driver_id, expected_res',
                             [
                                 ('json', 'CLS', expected_driver_json),
                                 ('xml', 'BHS', expected_driver_xml)
                             ])
    def test_drivers_api(self, api_format, driver_id, expected_res, client):
        with patch('Flask_app.views.api_endpoints.Report.build_report', return_value=self.test_example):
            return_value = client.get(
                f'http://127.0.0.1:5000/api/v1/report/driver/?format={api_format}&driver_id={driver_id}')

        assert return_value.status_code == 200
        assert return_value.data == expected_res
