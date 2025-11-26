from datetime import datetime

class SaveDTRLog:
    def __init__(self, ouid: int, scanning_no: str, log_date: datetime, action_type: int) -> None:
        self.DTRFileId: int = 0
        self.ItemNo: int = 0
        self.ScanningNo = scanning_no
        self.LogDate =  log_date
        self.DeviceId: str = ''
        self.ActionTypeId: int = action_type
        self.Value5: int = 0
        self.Value6: int = 0
        self.OUID: int = ouid

    def gen_save_dtr_log_payload(self):
        return {
                'DTRFileId': self.DTRFileId,
                'ItemNo': self.ItemNo,
                'ScanningNo': self.ScanningNo,
                'LogDate': self.LogDate.isoformat(),  # Convert datetime to ISO string
                'DeviceId': self.DeviceId,
                'ActionTypeId': self.ActionTypeId,
                'Value5': self.Value5,
                'Value6': self.Value6,
                'OUID': self.OUID
            }

    def gen_set_employee_attendance_payload(self):
        return {
                'ScanningNo': self.ScanningNo,
                'AttendanceDate': self.LogDate.isoformat(),  # Convert datetime to ISO string
            }
