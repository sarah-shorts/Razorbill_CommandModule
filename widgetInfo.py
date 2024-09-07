blk = "#000000"
blu = "#0008FF"
red = "#FF0000"
dgr = "#006806"

guiFields = {
    "border0": {
        "type": 'T',
        "label": '=============================================================================================================================================================',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "Opening": {
        "type": 'T',
        "label": ' -= Ma\'ii Setup =- \n A Basic Strain Experiment Assistant',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "border1": {
        "type": 'T',
        "label": '=============================================================================================================================================================',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blank01": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "openingtext": {
        "type": 'D',
        "label": 'Ma\'ii is a very basic assistant programmed to help control the operation of the Razorbill strain \n'+
                 'cell when installed within a Quantum Design PPMS. By setting the temperature/voltage parameters \n'+
                 'a simple experiment can be run that cycles the temperature while iteratively increasing the strain.',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blank02": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "d3Header": {
        "type": 'H',
        "label": 'D3 Temperature Profile Parameters',
        "units": '',
        "stats": '',
        "color": blu,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blanka": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "d3TempExp": {
        "type": 'TE',
        "label": '  Exp Type:  ',
        "units": '',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": ['Ramp', 'Multi'],
        "value": 'Ramp'
    },
    "d3FieldExp": {
        "type": 'TE',
        "label": '  Exp Type:  ',
        "units": '',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": ['Ramp', 'Multi'],
        "value": 'Ramp'
    },
    "T_max": {
        "type": 'E',
        "label": '  T_max:  ',
        "units": 'K',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [300, 1.8],
        "value": 300
    },
    "F_max": {
        "type": 'E',
        "label": '  F_max:  ',
        "units": 'Oe',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [90000, -90000],
        "value": 90000
    },
    "T_min": {
        "type": 'E',
        "label": '  T_min:  ',
        "units": 'K',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [300, 1.8],
        "value": 1.8
    },
    "F_min": {
        "type": 'E',
        "label": '  F_min:  ',
        "units": 'Oe',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [90000, -90000],
        "value": -90000
    },
    "T_rate": {
        "type": 'E',
        "label": '  T_rate:  ',
        "units": 'K/min',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [10, 0.1],
        "value": 5
    },
    "F_rate": {
        "type": 'E',
        "label": '  F_rate:  ',
        "units": 'Oe/min',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [100, 1],
        "value": 10
    },
    "T_max2": {
        "type": 'E',
        "label": '  T_max2:  ',
        "units": 'K',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [300, 1.8],
        "value": 300
    },
    "F_max2": {
        "type": 'E',
        "label": '  F_max2:  ',
        "units": 'Oe',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [90000, -90000],
        "value": -90000
    },
    "T_min2": {
        "type": 'E',
        "label": '  T_min2:  ',
        "units": 'K',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [300, 1.8],
        "value": 1.8
    },
    "F_min2": {
        "type": 'E',
        "label": '  F_min2:  ',
        "units": 'Oe',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [90000, -90000],
        "value": 90000
    },
    "T_rate2": {
        "type": 'E',
        "label": '  T_rate2:  ',
        "units": 'K/min',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [10, 0.1],
        "value": 5
    },
    "F_rate2": {
        "type": 'E',
        "label": '  F_rate2:  ',
        "units": 'Oe/min',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [100, 1],
        "value": 10
    },
    "blank1": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "d3FieldHeader": {
        "type": 'H',
        "label": 'D3 Field Profile Parameters',
        "units": '',
        "stats": '',
        "color": blu,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "d3TempHeader": {
        "type": 'H',
        "label": 'D3 Temp Profile Parameters',
        "units": '',
        "stats": '',
        "color": blu,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blankb": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "H_field": {
        "type": 'E',
        "label": '  H_field:  ',
        "units": 'Oe',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [140000, 0],
        "value": 0
    },
    "Temp": {
        "type": 'E',
        "label": '  Temp:  ',
        "units": 'K',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [300, 1.8],
        "value": 2
    },
    "blank2": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "rzExpHeader": {
        "type": 'H',
        "label": 'Razorbill Strain Profile Parameters',
        "units": '',
        "stats": '',
        "color": blu,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blankc": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "rzExp": {
        "type": 'TE',
        "label": '  Exp Type:  ',
        "units": '',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": ['Tens.', 'Comp.'],
        "value": 'Tens.'
    },
    "V_CH1": {
        "type": 'E',
        "label": '  V_CH1:  ',
        "units": 'V',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [120, 0],
        "value": 50
    },
    "V_CH2": {
        "type": 'E',
        "label": '  V_CH2:  ',
        "units": 'V',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [0, -50],
        "value": 0
    },
    "V_steps": {
        "type": 'E',
        "label": '  V_steps:  ',
        "units": 'steps',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [100, 5],
        "value": 5
    },
    "V_skip": {
        "type": 'E',
        "label": '  V_skip:  ',
        "units": '#',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [5, 0],
        "value": 0
    },
    "V_rate": {
        "type": 'E',
        "label": '  V_rate:  ',
        "units": 'V/s',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [1.0, 0.1],
        "value": 0.1
    },
    "blank4": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "compHeader": {
        "type": 'H',
        "label": 'Compliance and Safety Status:',
        "units": '',
        "stats": '',
        "color": blu,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blanke": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "complianceStatus": {
        "type": 'S',
        "label": 'Continue',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "endExplanation": {
        "type": 'Tinline',
        "label": 'If you are finished with experimental parameter entry, check for any red values. Revise them, \n'
                 'and when complete, press "Continue." This will start the control and data collection \n'
                 'through the Razorbill, PPMS, Capacitance Bridge, and Power Supply.',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blankf": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "nextStep": {
        "type": 'BO',
        "label": 'Continue',
        "units": 'V',
        "stats": 'Holding Default Value',
        "color": blk,
        "bounds": [120, 0],
        "value": 50
    },
    "blank5": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    },
    "blank6": {
        "type": 'B',
        "label": '',
        "units": '',
        "stats": '',
        "color": blk,
        "bounds": ['n/a', 'n/a'],
        "value": ''
    }
}

monitorFields = {
    "border0": {
        "type": 'T',
        "label": '=============================================================================================================================================================',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "Opening": {
        "type": 'T',
        "label": ' -= Ma\'ii Monitor =- \n Watching experiment in progress',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "border1": {
        "type": 'T',
        "label": '=============================================================================================================================================================',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "blank01": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "openingtext": {
        "type": 'D',
        "label": 'Experiment running..!',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "blank02": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "d3Header": {
        "type": 'H',
        "label": 'MultiVu D3 Parameters',
        "units": '',
        "status": '',
        "color": blu,
        "value": '',
        "format": ''
    },
    "blankb": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "Temperature": {
        "type": 'S',
        "label": 'Temperature:',
        "units": 'K',
        "status": '',
        "color": blk,
        "value": 0,
        "format": '2'
    },
    "Field": {
        "type": 'S',
        "label": 'Magnetic Field:',
        "units": 'Oe',
        "status": '',
        "color": blk,
        "value": 0,
        "format": '1'
    },
    "blankg": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "capHeader": {
        "type": 'H',
        "label": 'Andeen Hagerling Parameters',
        "units": '',
        "status": '',
        "color": blu,
        "value": '',
        "format": ''
    },
    "blankc": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "Capacitance": {
        "type": 'S',
        "label": 'Capacitance:',
        "units": 'pF',
        "status": '',
        "color": blk,
        "value": 0,
        "format": '7'
    },
    "blanky": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "rzHeader": {
        "type": 'H',
        "label": 'Razorbill Power Supply Parameters',
        "units": '',
        "status": '',
        "color": blu,
        "value": '',
        "format": ''
    },
    "blankf": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "CH1Voltage": {
        "type": 'S',
        "label": 'CH1 Voltage:',
        "units": 'V',
        "status": '',
        "color": blk,
        "value": 0,
        "format": '2'
    },
    "CH2Voltage": {
        "type": 'S',
        "label": 'CH2 Voltage:',
        "units": 'V',
        "status": '',
        "color": blk,
        "value": 0,
        "format": '2'
    },
    "blankw": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "measureHeader": {
        "type": 'H',
        "label": 'Program Internal State:',
        "units": '',
        "status": '',
        "color": blu,
        "value": '',
        "format": ''
    },
    "blankq": {
        "type": 'B',
        "label": '',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
    "measureStatus": {
        "type": 'DS',
        "label": 'Status:',
        "units": '',
        "status": '',
        "color": blk,
        "value": '',
        "format": ''
    },
}