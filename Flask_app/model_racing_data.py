from my_custom_report import Report
from Flask_app.db_models import db, Driver, RacingReport

report_inst = Report()
REPORT_PATH = '../data/racing_data'


def create_tables():
    with db:
        db.create_tables([Driver, RacingReport])


class ReportDB:
    @staticmethod
    def fill_db(path_to_report=REPORT_PATH):
        report = report_inst.build_report(path_to_report)

        for driver_abbr, data in report.items():
            dr = Driver.create(abbr=driver_abbr, name=data['name'], org=data['org'])
            RacingReport.create(driver=dr, lap_time=data['lap_time'])

    @classmethod
    def get_report(cls, order=None) -> dict:
        report = {}
        query = RacingReport\
            .select(RacingReport, Driver)\
            .join(Driver)

        if order:
            report_data = cls.get_ordered_report(query, order)
        else:
            report_data = query

        for data in report_data:
            report[data.driver.abbr] = {
                'name': data.driver.name,
                'org': data.driver.org,
                'lap_time': data.lap_time
            }

        return report

    @classmethod
    def get_ordered_report(cls, query, order):
        if order == 'asc':
            report_data = query.order_by(RacingReport.lap_time)
        else:
            report_data = query.order_by(RacingReport.lap_time.desc())

        return report_data
