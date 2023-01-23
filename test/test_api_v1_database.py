import unittest
from unittest.mock import patch
from Flask_app.app import app
import Flask_app.racing_data as racing_data


class TestAPI(unittest.TestCase):
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

    expected_json = b'{"CLS": {"name": "Charles Leclerc", "org": "SAUBER FERRARI", "lap_time": "1:12.829"}, ' \
                    b'"BHS": {"name": "Brendon Hartley", "org": "SCUDERIA TORO ROSSO HONDA", "lap_time": "1:13.179"}}'

    expected_json_desc = b'{"BHS": {"name": "Brendon Hartley", "org": "SCUDERIA TORO ROSSO HONDA", "lap_time": "1:13.179"}, ' \
                    b'"CLS": {"name": "Charles Leclerc", "org": "SAUBER FERRARI", "lap_time": "1:12.829"}}'

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

    expected_xml_desc = b"""<results>
  <BHS>
    <lap_time>1:13.179</lap_time>
    <name>Brendon Hartley</name>
    <org>SCUDERIA TORO ROSSO HONDA</org>
  </BHS>
  <CLS>
    <lap_time>1:12.829</lap_time>
    <name>Charles Leclerc</name>
    <org>SAUBER FERRARI</org>
  </CLS>
</results>"""

    expected_driver_json = b'{"name": "Charles Leclerc", "org": "SAUBER FERRARI", "lap_time": "1:12.829"}'
    expected_driver_xml = b"""<results>
  <name>Brendon Hartley</name>
  <org>SCUDERIA TORO ROSSO HONDA</org>
  <lap_time>1:13.179</lap_time>
</results>"""

    models = [racing_data.Driver, racing_data.RacingReport]

    @classmethod
    @patch('Flask_app.racing_data.Report.build_report', return_value=test_example)
    @patch.object(racing_data.db, 'database', ':memory:')
    def setUpClass(cls, report_patcher):
        racing_data.db.connect()
        racing_data.db.create_tables(cls.models)

        cls.report_db = racing_data.ReportDB()
        cls.report_db.fill_db()

        cls.client = app.test_client()

    def test_one(self):
        res = self.report_db.get_report()
        exp = self.test_example
        self.assertEqual(exp, res)

    def test_api_v1(self):
        for api_format, exp_res in (('json', self.expected_json), ('xml', self.expected_xml)):
            with self.subTest():
                return_value = self.client.get(f'http://127.0.0.1:5000/api/v1/report/?format={api_format}')

                self.assertEqual(exp_res, return_value.data)

    def test_api_v1_order(self):
        for api_format, order, exp_res in (('json', 'asc', self.expected_json),
                                           ('json', 'desc', self.expected_json_desc),
                                           ('xml', 'asc', self.expected_xml),
                                           ('xml', 'desc', self.expected_xml_desc)):
            with self.subTest():
                return_value = self.client\
                    .get(f'http://127.0.0.1:5000/api/v1/report/?format={api_format}&order={order}')

                self.assertEqual(return_value.status_code, 200)
                self.assertEqual(return_value.data, exp_res)

    def test_api_v1_error(self):
        return_value = self.client.get('http://127.0.0.1:5000/api/v1/report/?format=wrong_format')
        self.assertEqual(return_value.status_code, 400)

    def test_drivers_api(self):
        for api_format, driver_id, expected_res in (('json', 'CLS', self.expected_driver_json),
                                                    ('xml', 'BHS', self.expected_driver_xml)):
            with self.subTest():
                return_value = self.client.get(
                    f'http://127.0.0.1:5000/api/v1/report/driver/?format={api_format}&driver_id={driver_id}')

                self.assertEqual(return_value.status_code, 200)
                self.assertEqual(return_value.data, expected_res)

    def test_drivers_api_error(self):
        for api_format, driver_id, exp_res in (('wrong_format', 'CLS', 400),
                                               ('json', 'wrong_id', 500)):
            with self.subTest():
                return_value = self.client.get(
                            f'http://127.0.0.1:5000/api/v1/report/driver/?format={api_format}&{driver_id}')

                self.assertEqual(return_value.status_code, exp_res)

    @classmethod
    def tearDownClass(cls):
        racing_data.db.drop_tables(cls.models)
        racing_data.db.close()
