# Required to communicate with the QD machine/instrument
from QDInst import QDInstrument



# Communicating with the QD machine/instrument
while True:
    # To poll a new set of readings from the QD machine, QDInstrument() must be invoked
    QDI = QDInstrument()

    # From this reading, the temperature, field, and chamber parameters can be extracted
    #QDI.temp # Current temperature of machine {float}
    #QDI.temp_status_code # Temp status code {int}
    #QDI.temp_status # Human-readable temp status description {str}
    #QDI.temp_unit # Returns a string of "K" to indicate kelvin units {str}
    #print(f"The temperature is {QDI.temp} {QDI.temp_unit}; status is {QDI.temp_status}")


    QDI.field # Current applied field of machine {float}
    print(QDI.field_status_code) # Field status code {int}
    print(QDI.field_status) # Human-readable field status description {str}
    QDI.field_unit # Returns a string of "Oe" to indicate oersted units {str}
    #print(f"The field is at {QDI.field} {QDI.field_unit}; status is {QDI.field_status}")

    #QDI.chamber_status_code # Chamber status code {int}
    #QDI.chamber_status # Human-readable chamber status description {str}
    #print(f"The chamber status is {QDI.chamber_status}")

