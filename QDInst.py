import win32com.client
import pythoncom
from DetectMultiVu import Instrument, MultiVuExeException
import sys


class QDInstrument:
    def __init__(self):
        if sys.platform == 'win32':
            try:
                self._mvu = win32com.client.Dispatch(Instrument(verbose=True).classId)
            except AttributeError:
                pass
        else:
            raise Exception('This must be running on a Windows machine')

        self.temp_unit = "K"
        self.field_unit = "Oe"

        # Instantiate the 'set' class
        self.set = QDInstrument._set()

    def _get_temp_status(self):
        temperature = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0)
        temp_status_code = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0.0)
        temp_err = self._mvu.GetTemperature(temperature, temp_status_code)
        TempStates = {
            "1": "Stable",
            "2": "Tracking",
            "5": "Near",
            "6": "Chasing",
            "7": "Pot Operation",
            "10": "Standby",
            "13": "Diagnostic",
            "14": "Impedance Control Error",
            "15": "General Failure",
        }
        return temperature.value, TempStates[str(temp_status_code.value)], temp_err
    
    def _get_field_status(self):
        field = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0)
        field_status_code = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0.0)
        field_err = self._mvu.GetField(field, field_status_code)
        MagStates = {
            "0": "Undefined",
            "1": "Stable",
            "2": "Switch Warming",
            "3": "Switch Cooling",
            "4": "Holding (Driven)",
            "5": "Iterate",
            "6": "Ramping",
            "7": "Ramping",
            "8": "Resetting",
            "9": "Current Error",
            "10": "Switch Error",
            "11": "Quenching",
            "12": "Charging Error",
            "14": "PSU Error",
            "15": "General Failure",
        }
        return field.value, MagStates[str(field_status_code.value)], field_err

    @property
    def field(self):
        return self._get_field_status()[0]
    
    @property
    def field_status(self):
        return self._get_field_status()[1]
    
    @property
    def temp(self):
        return self._get_temp_status()[0]
    
    @property
    def temp_status(self):
        return self._get_temp_status()[1]


    @property
    def chamber_status(self):
        chamber_status_code = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        chamber_err = self._mvu.GetChamber(chamber_status_code)
        ChamberStates = {
            "0": "Sealed",
            "1": "Purged and Sealed",
            "2": "Vented and Sealed",
            "3": "Sealed",
            "4": "Performing Purge/Seal",
            "5": "Performing Vent/Seal",
            "6": "Pre-HiVac",
            "7": "HiVac",
            "8": "Pumping Coninuously",
            "9": "Flooding Continuously",
            "14": "HiVac Error",
            "15": "General Failure",
        }
        return ChamberStates[int(chamber_status_code)], chamber_err


    class _set:
        def __init__(self):
            self._mvu = win32com.client.Dispatch(Instrument(verbose=False).classId)

        def temp(self, temperature, rate, approach):
            err = self._mvu.SetTemperature(temperature, rate, approach)
            return err
            # Approach Options: Fast Settle (0); No O'Shoot (1).

        def field(self, field, rate, approach, mag_state):
            err = self._mvu.SetField(field, rate, approach, mag_state)
            return err
            # Approach Options: Linear (0); No O'Shoot (1); Oscillate (2).
            # Magnet State Options: Persistent (0); Driven (1).

        def chamber(self, code):
            err = self._mvu.SetChamber(code)
            return err