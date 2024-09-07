import pyvisa


rm = pyvisa.ResourceManager() 

print(rm)
print(rm.list_resources())



inst = rm.open_resource('ASRL10::INSTR')

print(inst.query("*IDN?"))