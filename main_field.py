# import pyvisa from NI instruments
import csv
import tkinter.filedialog

import pyvisa
# import QDInst to gain access to MultiVu
from QDInst import QDInstrument\

# import calls required for GUI creation
from tkinter import *
import tkinter as tk
from functools import partial
import math
from widgetInfo_field import guiFields
from widgetInfo_field import monitorFields
from tkinter import messagebox
import time

# import calls for the directory finder
import os
from statistics import mean

class MinMaxError(Exception):
    pass


class RangeError(Exception):
    pass


class ListDimensionError(Exception):
    pass


class StateException(Exception):
    pass


class VoltListError(Exception):
    pass


class RazorbillProgrammer (object):
    """
    This class is basically the entire GUI for the Ma'ii strain measurement assistant. There are various phases
    that the GUI passes between... an Intro... a Setup... a Monitor... a Conclusion. Currently this is very
    restricted and the functionalities are minimal. After all, what can you do with minimal GUI/program design
    experience ;)

    Why Ma'ii? Well I noticed lots of programs get named after the Greek myths... so I thought it would be nice
    to use a native american mythos instead.

    Any glitches and whatnot can be passed here:
    www.right_in_the_bin_not_a_real_email.com
    """

    def __init__(self):
        """ Setup parameters that will be used throughout the GUI and program """
        self.root = Tk()

        # define a field stabilization time here (seconds). This is the time the program waits after the dynacool is stable and before starting to measure.
        self.wait_t = 180

        #For first measuremnet range
        self.wait_t1 = 180
        #For second measuremnet range
        self.wait_t2 = 180

        # define some colors so we don't have to remember hex codes
        self.blk = "#000000"
        self.blu = "#0008FF"
        self.red = "#FF0000"
        self.dgr = "#006806"
        self.gry = "#808080"

        # boolean values used for flow control
        self.tempChange = False
        self.tempExpWasRamp = False
        self.voltModeChange = False
        self.inCompliance = True
        self.inIntro = False
        self.inExpSetup = False
        self.inDirectoryGet = False
        self.inMonitor = False
        self.monitorState = "Initial"
        self.voltListError = False
        self.programEnd = False
        self.modeCounter = 1
        self.rampMax = 8
        self.isMeasuring = False
        self.refreshCounter = 0
        self.multiVuCrash = False

        # parameter dictionary, also used to display fields in Ma'ii Experiment Setup page
        self.guiDict = guiFields
        self.monDict = monitorFields
        gui_cols = range(len(next(iter(guiFields))))
        gui_rows = range(len(guiFields))
        self.setup_widgets = [[tk.Entry(self.root) for i in gui_cols] for j in gui_rows]
        mon_cols = range(len(next(iter(guiFields))))
        mon_rows = range(len(guiFields))
        self.monitor_widgets = [[tk.Entry(self.root) for i in mon_cols] for j in mon_rows]

        # move to the first part of the program
        self.inIntro = True

        # create instance of the PPMS instrument
        self.D3 = QDInstrument()

        # create instance of the cap bridge
        self.rm = pyvisa.ResourceManager()
        self.ANDY = self.rm.open_resource('GPIB0::28::INSTR') #AH capicitance bridge
        self.SPARKY = self.rm.open_resource('ASRL10::INSTR') #Razorbill power supply RP100

        # voltage tables
        self.v_table = []
        self.v_table_i = 0

        # puppers
        self.pup1 = PhotoImage(file=r"pupper1_smol.png")
        self.pup2 = PhotoImage(file=r"pupper2_smol.png")
        self.pup3 = PhotoImage(file=r"pupper3_smol.png")
        self.pupper_counter = 0

        # file stream saves
        self.maii_save_stream = ""
        self.qd_open_file = ""
        self.c_table = []
        self.v1_table = []
        self.v2_table = []
        self.ti = 0.         
        self.tcounter = 1.   
        self.need_header = True
        self.found_data = False
        self.timeline = 0

    def navigate_browse(self, param):
        """ This function allows us to use the OS to browse for a file """
        print("we're looking for a {param}".format(param=param))

        if param == "Open":
            fname = tkinter.filedialog.askopenfilename(filetypes=(("MultiVu Dat Files", "*.dat"), ("All files", "*")))
            self.qd_open_file = fname
            print('we have the open stream...'+fname)
        elif param == "Save":
            fname = tkinter.filedialog.asksaveasfilename(filetypes=(("Ma'ii Dat Files", "*.csv"), ("All files", "*")))
            self.maii_save_stream = fname
            try:
                if self.maii_save_stream.split('.')[-1] != "csv":
                    self.maii_save_stream = self.maii_save_stream+".csv"
            except:
                pass
            print('we have the open stream...'+self.maii_save_stream)

    def navigate_continue(self):
        """ This function controls the flow to the measurement phase """

        if ".dat" not in self.qd_open_file:
            print("I can\'t allow you to do that Jim...")
            messagebox.showerror("No valid QD input stream!", "Oh...\n I can\'t allow you to do that Jim...")
        elif ".csv" not in self.maii_save_stream:
            print("I can\'t allow you to do that Jim...")
            messagebox.showerror("No valid Ma'ii save stream!", "Oh...\n I can\'t allow you to do that Jim...")
        else:
            # if the user clicks yes, continue...
            if messagebox.askyesno("Here we go...!", "Would you like to continue to the measurement phase?\n\n"
                                                     "It looks like you have defined both the input and output!\n"
                                                     "These files will be populated automatically by the program."):
                # destroy the current window
                self.root.update()
                self.root.destroy()
                # set control parameters to move onto next phase
                self.inDirectoryGet = False
                self.inMonitor = True
                self.run()
            # if the user backs out
            else:
                # do nothing
                pass

    def navigate_fileloc(self):
        """
        This function call is placed between the setup and measurement phases, and is intended to have the
        user perform a few actions on the Dynacool, (e.g. starting a ETO run continuously), and then proceeding
        to navigate to the ETO output file, and then to also define a Ma'ii output file. Ma'ii will interweave
        the data collected from the strain bridge into the QD.dat file
        """

        try:
            self.root.update()
            self.root.destroy()
        except:
            print("something bad happened with kill root")

        self.root = Tk()
        self.root.title("Ma'ii Navigator")

        intro_text = "-= Ma'ii Navigator =- \n\n" \
                        "In order for Ma'ii to make data collection as painless as possible, please\n"\
                        "complete the following tasks to set up the ETO and File Dependencies...\n"\

        intro = tk.Label(self.root, text=intro_text, width=58)
        intro.config(font=('arial', 12), fg=self.blk)
        intro.grid(row=0, column=0, columnspan=8)

        header = tk.Label(self.root, text="Please read instructions!", width=58)
        header.config(font=('arial', 12), fg=self.blu)
        header.grid(row=1,columnspan=8)

        instru_text = "1) Within MultiVu, activate the .seq file Razorbill_Measure_ETO_Continously\n" \
                        "2) Using the 'Browse QD' button, navigate to the output file from ETO\n" \
                        "3) Using the 'Browse Ma'ii' button, navigate and name desired output file\n" \

        instru = tk.Label(self.root, text=instru_text, width=58)
        instru.config(font=('arial', 12), fg=self.blk, anchor=W, justify=LEFT)
        instru.grid(row=2,columnspan=8)

        instru2_text = "When complete, hit the 'Continue' button.\n"

        instru2 = tk.Label(self.root, text=instru2_text, width=58)
        instru2.config(font=('arial', 12), fg=self.blk, anchor=W, justify=LEFT)
        instru2.grid(row=3,columnspan=8)

        browseQD = tk.Label(self.root, text="Navigate QD file:", width=30)
        browseQD.config(font=('arial', 12), fg=self.blk, anchor=W)
        browseQD.grid(row=4, column=0, columnspan=2)

        ptBrowseQD = partial(self.navigate_browse, "Open")
        QDButton = tk.Button(master=self.root, text='Browse QD file', width=15, command=ptBrowseQD)
        QDButton.config(anchor=W)
        QDButton.grid(row=4, column=1, columnspan=2)

        browseM = tk.Label(self.root, text="Navigate Ma\'ii file:", width=30)
        browseM.config(font=('arial', 12), fg=self.blk, anchor=W)
        browseM.grid(row=5, column=0, columnspan=2)

        ptBrowseM = partial(self.navigate_browse, "Save")
        MButton = tk.Button(master=self.root, text='Browse Ma\'ii file:', width=15, command=ptBrowseM)
        MButton.config(anchor=W)
        MButton.grid(row=5, column=1, columnspan=2)

        instru3_text = "\n"

        instru3 = tk.Label(self.root, text=instru3_text, width=58)
        instru3.config(font=('arial', 12), fg=self.blk, anchor=W, justify=LEFT)
        instru3.grid(row=6,columnspan=8)

        fintext = tk.Label(self.root, text="Continue to measure:", width=30)
        fintext.config(font=('arial', 12), fg=self.blk, anchor=W)
        fintext.grid(row=7, column=0, columnspan=2)

        finbutton = tk.Button(master=self.root, text='Continue', width=15, command=self.navigate_continue)
        finbutton.config(anchor=W)
        finbutton.grid(row=7, column=1, columnspan=2)

    def intro_create(self):
        """ This definition just creates a basic intro page, then kills it """

        try:
            self.root.update()
            self.root.destroy()
        except:
            print("something bad happened with kill root")

        self.root = Tk()

        self.root.title("Ma\'ii")

        # given the dictionary, we can define a widget list of placeholders
        self.setup_widgets = [[tk.Entry(self.root) for i in range(2)] for j in range(3)]

        photo = PhotoImage(file=r"C:\Users\sysadmin\Desktop\Razorbill-WilsonGroup\Razorbill_CommandModule\Intro.png")
        photo_label = Label(image=photo, width=750)
        photo_label.grid(row=0, column=0)
        photo_label.image = photo

        pt_intro_function = partial(self.intro_continue_next)
        self.setup_widgets[0][1] = tk.Button(text="Continue", command=pt_intro_function, width=30)
        self.setup_widgets[0][1].config(font=('arial', 10), fg=self.blk)
        self.setup_widgets[0][1].grid(row=1, column=0)

    def intro_continue_next(self):

        if True:
            # if the user clicks yes, continue...
            if messagebox.askyesno("Here we go...!", "Would you like to continue to the setup phase?\n\n "
                                                     "This program was developed for the TEMPO facility at\n"
                                                     "the University of California, Santa Barbara.\n\n"
                                                     "Please note that use of this program comes with \n"
                                                     "no guarantees and no liability for error.\n\n"):
                # destroy the current window
                self.root.update()
                self.root.destroy()
                # set control parameters to move onto next phase
                self.inIntro = False
                self.inExpSetup = True
                self.run()
            # if the user backs out
            else:
                # do nothing
                pass

    def monitor_determine_state(self):
        """
        This definition determines and sets the state function so that we know what the PPMS is doing
        and what states we should set for the Razorbill... there are effectively 5 states that we have
        to worry about..

        "Hold" indicates that there will never be any ramping temperature, effectively bypassing any
        temperature calls

        "Initial" should only ever be set at the beginning and flags the program to ramp the ppms
        to the 0 Oe at the 100 Oe/min and cool to Temp. Then ramp to Fmin. It should immediately be replaced by monitor_determine_state afterwards

        "Ready" indicates that the ppms is stable and has equilibrated at the Fmin and Temp... this indicates that
        we should begin a new strain value and restart a ramping cycle

        "Busy" indicates that the ppms is either in the 'chasing' or 'near' conditions. In this event, we
        will effectively pass control back to the monitor and perform no changes

        "Finished" indicates that the ppms is sitting at Fmax and is stable, indicating that we need to ramp
        back down to Fmin. The rest of the control is relinquished to the "Ready" state to set the next strain.

        NOTE: ADD A STATE OR SOMETHING TO WRITE AND DETERMINE WHAT THE MEASUREMENT STATE IS TO EASILY
        DELINIATE WHEN A MEAUREMENT IS BEING TAKEN (E.G. HEATING AND MEASURING) FOR EASY PLOTTING
        """

        fmax = self.guiDict.get("F_max").get("value")
        fmin = self.guiDict.get("F_min").get("value")
        fmax2 = self.guiDict.get("F_max2").get("value")
        fmin2 = self.guiDict.get("F_min2").get("value")
        mode = self.guiDict.get("d3FieldExp").get("value")
        ftol = 2 #Oersted
        #print(str(tmin + ttol) + ">="+ str(self.D3.temp) + ">="+str(tmin - ttol))
        if mode == "Ramp" or mode == "Hold":
            try:
                if self.monitorState == "Initial":
                    print("The ppms is in the initial state")
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the INITIAL state. \n"
                                                                   "Voltages should be 0. Will now begin field\n"
                                                                   "equilibration to F_min and Temp choice."})

                # if we have a stable field and we're within tolerance to F_min, we're in the Ready state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((0+ftol) >= self.D3.field >= (0-ftol)):
                    print(f'waiting {self.wait_t/60} min')
                    self.monDict["measureStatus"].update({"value": "Ma'ii is waiting for field stabilization. \n"
                                                                   f'time to wait: {self.wait_t/60}'
                                                                   })
                    time.sleep(self.wait_t)                 #Wait to stabilize before making a measurment
                    self.monitorState = "Ready"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the READY state. \n"
                                                                   "We are ready to begin another strain increment\n"
                                                                   "and begin a new field ramp profile."})
                    
                # if we have a stable field and we're within tolerance to f_max, we're in the Finished state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((fmax+ftol) >= self.D3.field >= (fmax-ftol)):
                    self.monitorState = "Finished"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the FINISHED state. \n"
                                                                   "A strain measurement has completed and we are \n"
                                                                   "ready to begin ramping back to fmin Oe."})
                    
                # if we have a changing field we wait for stabilization
                elif self.D3.field_status in ["Holding (Driven)", "Ramping", "Iterating"] and self.D3.temp_status in ["Tracking", "Chasing"]:
                    self.monitorState = "Busy"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the BUSY state. \n "
                                                                   "We are ramping to base field, or a strain measurement\n"
                                                                   "is running as we ramp to the max field."})
                elif self.D3.field_status in ["Ramping", "Iterating"] and self.D3.temp_status in ["Stable", "Tracking", "Chasing"]:
                    self.monitorState = "Busy"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the BUSY state. \n "
                                                                   "We are ramping to base field, or a strain measurement\n"
                                                                   "is running as we ramp to the max field."})
                else:
                    print(self.D3.field_status)
                    raise StateException

            except StateException:
                print("Something has gone very wrong and we've gone into an undefined state")

        elif mode == "Multi":
            #print('using multi state determination')
            try:
                if self.monitorState == "Initial":
                    print("The ppms is in the initial state")
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the INITIAL state. \n"
                                                                   "Voltages should be 0. Will now begin temperature\n"
                                                                   "equilibration to F_min and Temp choice."})

                # if we have a stable field and we're within tolerance to f_min1, we're in the Ready1 state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((fmin + ftol) >= self.D3.field >= (fmin - ftol)):

                    print(f'waiting {self.wait_t1/60} min')
                    self.monDict["measureStatus"].update({"value": "Ma'ii is waiting for thermalization. \n"
                                                                   f'time to wait: {self.wait_t1/60}'
                                                                })
                    time.sleep(self.wait_t1)                 #Wait to thermalize before making a measurment
                    self.monitorState = "Ready1"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the READY1 state. \n"
                                                                   "We are ready to begin another strain increment\n"
                                                                   "and begin a new field ramp profile."})
                # if we have a stable field and we're within tolerance to f_min1, we're in the Ready1 state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((fmin2 + ftol) >= self.D3.field >= (fmin2 - ftol)):

                    print(f'waiting {self.wait_t2/60} min')
                    self.monDict["measureStatus"].update({"value": "Ma'ii is waiting for thermalization. \n"
                                                                   f'time to wait: {self.wait_t2/60}'
                                                                   })
                    time.sleep(self.wait_t2)                 #Wait to thermalize before making a measurment
                    self.monitorState = "Ready2"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the READY2 state. \n"
                                                                   "We are ready to begin another strain increment\n"
                                                                   "and begin a new field ramp profile."})
                # if we have a stable field and we're within tolerance to f_max, we're in the Finished state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((fmax + ftol) >= self.D3.field >= (fmax - ftol)):
                    self.monitorState = "Finished1"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the FINISHED1 state. \n"
                                                                   "A strain measurement has completed and we are \n"
                                                                   "ready to begin ramping back to base field."})
                # if we have a stable field and we're within tolerance to f_max, we're in the Finished state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)"] and ((fmax2 + ftol) >= self.D3.field >= (fmax2 - ftol)):
                    self.monitorState = "Finished2"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the FINISHED2 state. \n"
                                                                   "A strain measurement has completed and we are \n"
                                                                   "ready to begin ramping back to base field."})
                # if we have a stable field and we're within tolerance to f_max, we're in the Finished state.
                elif self.D3.field_status in ["Stable", "Holding (Driven)","Ramping", "Iterating"]:
                    self.monitorState = "Busy"
                    self.monDict["measureStatus"].update({"value": "Ma'ii is in the BUSY state. \n "
                                                                   "We are cooling to base, or a strain measurement\n"
                                                                   "is running as we ramp the max field."})
                else:
                    print(self.D3.field_status)
                    raise StateException

            except StateException:
                print("Something has gone very wrong and we've gone into an undefined state")

    def monitor_set_voltage(self):
        """
        This definition controls the setting of voltages to the razorbill. At this point, the Vmax range and Vmin
        range for both piezo stacks is divided up based on the number of steps. Then we iterate the first stack
        through it's allowble values before invoking the second stack as well.
        """

        try:
            print("voltage index {index}".format(index=self.v_table_i))

            print("Aiming to use the voltage setpoint {value}".format(value=self.v_table[self.v_table_i]))
            time.sleep(1)

            print('Activating Ch1')
            time.sleep(1)
            self.SPARKY.write('outp1 1')
            print('Setting Ch1 Voltage to {value}'.format(value=self.v_table[self.v_table_i][0]))
            time.sleep(1)
            self.SPARKY.write('sour1:volt {value}'.format(value=self.v_table[self.v_table_i][0]))

            print('Activating Ch2')
            time.sleep(1)
            self.SPARKY.write('outp2 1')
            print('Setting Ch2 Voltage to {value}'.format(value=self.v_table[self.v_table_i][1]))
            time.sleep(1)
            self.SPARKY.write('sour2:volt {value}'.format(value=self.v_table[self.v_table_i][1]))

            self.v_table_i = self.v_table_i + 1

        except IndexError:
            print("we're probably done")
            self.programEnd = True

    def monitor_sparky_grounded(self):
        print('set ch1 volt to 0')
        time.sleep(0.1)
        self.SPARKY.write('sour1:volt 0')

        print('turn off chn 1')
        time.sleep(0.1)
        self.SPARKY.write('outp1 0')

        print('set ch2 volt to 0')
        time.sleep(0.1)
        self.SPARKY.write('sour2:volt 0')

        print('turn off chn 2')
        time.sleep(0.1)
        self.SPARKY.write('outp2 0')

        print('query both channels check that it did turn off')
        time.sleep(0.1)
        print(self.SPARKY.query('outp1?'))
        print(self.SPARKY.query('outp2?'))

        print('determine voltages')
        time.sleep(0.1)
        print(self.SPARKY.query('sour1:volt?'))
        print(self.SPARKY.query('sour2:volt?'))

    def monitor_control(self):
        """ This definition controls the PPMS, AH bridge, and power supply """

        fmax = self.guiDict.get("F_max").get("value")
        fmin = self.guiDict.get("F_min").get("value")
        frate = self.guiDict.get("F_rate").get("value")
        temp = self.guiDict.get("Temp").get("value")
        fmax2 = self.guiDict.get("F_max2").get("value")
        fmin2 = self.guiDict.get("F_min2").get("value")
        frate2 = self.guiDict.get("F_rate2").get("value")
        mode = self.guiDict.get("d3FieldExp").get("value")

        #print("d3 field state"+self.D3.field_status)

        if mode == "Ramp":
            # make sure we determine the state of the program
            self.monitor_determine_state()
            print(self.monitorState)

            # if we have a Initial situation
            if self.monitorState == "Initial":
                print("we are in the initial condition")

                # set power supply to known conditions
                self.monitor_sparky_grounded()

                # set field to ZFC conditions
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=0))
                self.D3.set.field(0, 100, 2, 1)

                # set temperature using T at 10K/min
                print('MultiVu command... go to {temp}K at {rate}K/min'.format(temp=temp, rate=10))
                self.D3.set.temp(temp, self.rampMax, 0)

                # change status to break from initial condition
                self.monitorState = "Unknown"

            # check if we're in the busy state
            elif self.monitorState == "Busy":
                #print("yo dont bother me you ass")
                pass

            # check if we're in the ready state
            elif self.monitorState == "Ready":
                print("we are stable at base and ready to set fields temps and strains")
                
                # set field to fmin
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin))
                self.D3.set.field(fmin, 100, 0, 1)

                # set the field state
                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set voltages eventually
                self.monitor_set_voltage()

                # set field using F_max and F_rate
                print('MultiVu command... go to {fmax}Oe at {rate}Oe/min'.format(fmax=fmax, rate=frate))
                self.D3.set.field(fmax, frate, 0, 1)
                self.isMeasuring = True

            # check if we're in the finished state
            elif self.monitorState == "Finished":

                print("the measurement has completed and we're ready to cool again")

                # set field to H_field ZFC condition
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin))
                self.D3.set.field(fmin, 100, 0, 1)

                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set temperature using T_min and T_rate
                #print('MultiVu command... go to {temp}K at {rate}K/min'.format(temp=tmin, rate=self.rampMax))
                #self.D3.set.temp(tmin, self.rampMax, 0)
                self.isMeasuring = False

        elif mode == "Multi":
            # make sure we determine the state of the program
            self.monitor_determine_state()
            print(self.monitorState)

            # if we have a Initial situation in T1 with R1
            if self.monitorState == "Initial":
                print("we are in the initial condition mode multi")

                # set power supply to known conditions
                self.monitor_sparky_grounded()

                # set field to ZFC conditions
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=0))
                self.D3.set.field(0, 100, 0, 1)

                # set temperature using T_min and T_rate
                print('MultiVu command... go to {temp}K at {rate}K/min'.format(temp=temp, rate=self.rampMax))
                self.D3.set.temp(temp, self.rampMax, 0)

                # change status to break from initial condition
                self.monitorState = "Unknown"

            # check if we're in the busy state
            elif self.monitorState == "Busy":
                print("yo dont bother me you ass (mode multi)")
                pass

            # check if we're in the ready state FOR REGIME 1
            elif self.monitorState == "Ready1":

                # we perform the measurement according to T1 and Ramp1
                print("we are stable at base and ready to set fields temps and strains")
                # set field to H_field
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin))
                self.D3.set.field(fmin, 100, 0, 1)

                # set the field state
                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set voltages eventually
                self.monitor_set_voltage()

                # set field using F_max and F_rate
                print('MultiVu command... go to {field}Oe at {rate}Oe/min'.format(field=fmax, rate=frate))
                self.D3.set.field(fmax, frate, 0, 1)
                self.isMeasuring = True


                # check if we're in the ready state for REGIME 2
            elif self.monitorState == "Ready2":

                # we perform the measurement according to F2 and Ramp1
                print("we are stable at base and ready to set fields temps and strains for the 2nd regime")
                # set field to H_field
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin2))
                self.D3.set.field(fmin2, 100, 0, 1)

                # set the field state
                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set temperature using F_max and F_rate
                print('MultiVu command... go to {field}K at {rate}K/min (regime 2)'.format(field=fmax2, rate=frate2))
                self.D3.set.temp(fmax2, frate2, 0, 1)
                self.isMeasuring = True



            # check if we're in the finished state
            elif self.monitorState == "Finished1":
                print("the measurement has completed and we're ready to move to regime 2")

                # set field to H_field ZFC condition
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin2))
                self.D3.set.field(fmin2, 100, 0, 1)

                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set temperature using T_min and T_rate
                #print('MultiVu command... go to {temp}K at {rate}K/min'.format(temp=tmin2, rate=self.rampMax))
                #self.D3.set.temp(tmin2, self.rampMax, 0)
                #self.isMeasuring = False

            # check if we're in the finished state
            elif self.monitorState == "Finished2":
                print("the measurement has completed and we're ready to ramp again to Fmin1")

                # set field to H_field ZFC condition
                print('MultiVu command... go to {field}Oe at 100Oe/min'.format(field=fmin))
                self.D3.set.field(fmin, 100, 0, 1)

                print("have to check for the field state")
                while self.D3.field_status != "Holding (Driven)":
                    print("we are waiting for field to catch up...")
                    time.sleep(1)
                print("field state reached")

                # set temperature using T_min and T_rate
                #print('MultiVu command... go to {temp}K at {rate}K/min'.format(temp=tmin, rate=self.rampMax))
                #self.D3.set.temp(tmin, self.rampMax, 0)
                self.isMeasuring = False

    def monitor_update_vals(self):
        """ This definition takes values from the peripherials and modifies the dictionaries accordingly """

        try:
            self.D3 = QDInstrument()
            #print("take temperature")
            #print(self.D3.temp)
            self.monDict["Temperature"].update({"status": self.D3.temp_status})
            self.monDict["Temperature"].update({"value": float(self.D3.temp)})
            #print("take field")
            self.monDict["Field"].update({"status": self.D3.field_status})
            self.monDict["Field"].update({"value": float(self.D3.field)})
        except:
            self.multiVuCrash = True
            print("Coms with D3 appear to have failed... try restarting multiVu to recover")
            while self.multiVuCrash:
                try:
                    self.D3 = QDInstrument()
                    # print("take temperature")
                    # print(self.D3.temp)
                    self.monDict["Temperature"].update({"status": self.D3.temp_status})
                    self.monDict["Temperature"].update({"value": float(self.D3.temp)})
                    # print("take field")
                    self.monDict["Field"].update({"status": self.D3.field_status})
                    self.monDict["Field"].update({"value": float(self.D3.field)})
                    self.multiVuCrash = False
                except:
                    print("still down... waiting 10s")
                    time.sleep(10)

        #print('take cap')
        try:
            cap_string = self.ANDY.query('FETCH').split("=")[2].strip().split()[0]
        except:
            print("ANDY is a little bitch")
            cap_string = 0.0000000

        self.monDict["Capacitance"].update({"value": float(cap_string)})

        volt1state = self.SPARKY.query('outp1?').strip()
        volt1 = float(self.SPARKY.query('sour1:volt?'))
        volt2state = self.SPARKY.query('outp2?').strip()
        volt2 = float(self.SPARKY.query('sour2:volt?'))
        if volt1state == "0":
            volt1state = "Latent"
        elif volt1state == "1":
            volt1state = "Active"
        if volt2state == "0":
            volt2state = "Latent"
        elif volt2state == "1":
            volt2state = "Active"
        self.monDict["CH1Voltage"].update({"status": volt1state})
        self.monDict["CH1Voltage"].update({"value": volt1})
        self.monDict["CH2Voltage"].update({"status": volt2state})
        self.monDict["CH2Voltage"].update({"value": volt2})

    def monitor_create(self):
        """ This definition creates the Ma'ii Experimental Monitor """

        try:
            #print("just killed root")
            self.root.destroy()
        except:
            pass
            #print("something bad happened with kill root")

        print("make new root")
        self.root = Tk()
        # Change the root title
        self.root.title("Ma\'ii Experimental Monitor")

        mon_cols = range(len(next(iter(guiFields))))
        mon_rows = range(len(guiFields))
        self.monitor_widgets = [[tk.Entry(self.root) for i in mon_cols] for j in mon_rows]

    def monitor_end_program(self):
        """ exit program by turning off powersupply and opening dialog """

        print("sequence has ended... turning off power supply.")

        self.monitor_sparky_grounded()

        if messagebox.showinfo("Program Finished", "Program has ended. Confirm exit."):
            # destroy the current window
            self.root.destroy()

    def monitor_writer(self):
        """
        This definition takes some values that have been updated in the dictionaries, it controls the matching
        of parameters from the Razorbill, cap bridge, and power supply with the output from the Dynacool
        and multiview... it requires the knowledge of the IOstreams defined in the directory GUI.
        """

        # grab the header data from the multivu file
        if self.need_header:
            with open(self.qd_open_file, 'r') as qdFile, open(self.maii_save_stream, 'a+', newline="") as miFile:
                for line in qdFile:
                    if line.strip() != "[Data]" and not self.found_data:
                        miFile.writelines(line)
                    elif line.strip() == "[Data]" and not self.found_data:
                        self.need_header = False
                        self.found_data = True
                        miFile.writelines(line)
                    elif line.strip() != "[Data]" and self.found_data:
                        myline = line.split(',')
                        print(myline)

                        cur_col = 0
                        for header in myline:
                            if "Time" in header:
                                print("The time variable is in the {col} column".format(col=cur_col))
                                self.timeline = cur_col
                                break
                            cur_col = cur_col + 1

                        myline.insert(0, "is Measuring?")
                        myline.insert(0, "Ch2 Voltage (V)")
                        myline.insert(0, "Ch1 Voltage (V)")
                        myline.insert(0, "Capacitance (pF)")

                        writer = csv.writer(miFile)
                        writer.writerow(myline)

                        #mystring = ""
                        #for item in myline:
                        #    mystring = mystring + item + ','

                        #miFile.writerow(myline)
                        #print(mystring)
                        break

        with open(self.qd_open_file, 'r') as qdFile:
            last_line = qdFile.readlines()[-1]
            #print("reading a line from {dir}".format(dir=self.qd_open_file))
            #print(last_line)
            last_table = last_line.split(",")
            #print("print first element from the dir .... time...? {ts}".format(ts=last_table[self.timeline]))
            tf = last_table[self.timeline]

        #print("ti is {ti}".format(ti=self.ti))
        #print("tf is {tf}".format(tf=tf))
        #print(self.ti == tf)
        #print(self.c_table)

        # initialize ti based on the first and only the first run
        if self.ti != tf and self.tcounter == 1:
            self.ti = tf
            self.tcounter = 0

        # actual logic for determining when to average the c, V1, v2 for each timestamp from MultiVu
        if self.ti == tf:
            try:
                c_i = float(self.monDict.get("Capacitance").get("value"))
                v1_i = float(self.monDict.get("CH1Voltage").get("value"))
                v2_i = float(self.monDict.get("CH2Voltage").get("value"))
                self.c_table.append(c_i)
                self.v1_table.append(v1_i)
                self.v2_table.append(v2_i)
            except TypeError:
                print("your c, v1, or v2 is fucked and not a number... invalidating tables")
                self.c_table = [0]
                self.v1_i = [0]
                self.v2_i = [0]
        # but if the timestamp has changed... we need to write the data to a file and reupdate things
        elif self.ti != tf and self.tcounter != 1:
            cbar = mean(self.c_table)
            v1bar = mean(self.v1_table)
            v2bar = mean(self.v2_table)
            last_table.insert(0, str(self.isMeasuring))
            last_table.insert(0, v2bar)
            last_table.insert(0, v1bar)
            last_table.insert(0, cbar)
            self.c_table = []
            self.v1_table = []
            self.v2_table = []
            try:
                c_i = float(self.monDict.get("Capacitance").get("value"))
                v1_i = float(self.monDict.get("CH1Voltage").get("value"))
                v2_i = float(self.monDict.get("CH2Voltage").get("value"))
                self.c_table.append(c_i)
                self.v1_table.append(v1_i)
                self.v2_table.append(v2_i)
            except TypeError:
                print("your c, v1, or v2 is fucked and not a number... invalidating tables")
                self.c_table = [0]
                self.v1_i = [0]
                self.v2_i = [0]
            self.ti = tf

            with open(self.maii_save_stream, 'a+', newline="") as miFile:
                writer = csv.writer(miFile)
                writer.writerow(last_table)
                print('writing to file')
                print(last_table)

    def monitor_update_screen(self):
        """ This definition controls screen updates when within the "monitor" side of Ma'ii """

        self.refreshCounter = self.refreshCounter + 1
        if self.refreshCounter % 25 == 0:
            print("Refresh screen to eliminate some weird glitches?")
            self.monitor_create()

        self.monitor_control()
        self.monitor_update_vals()
        self.monitor_writer()

        # the whole thing is effectively a loop... but each column/row may have different display parameters
        # in this event I split it apart for simplicity (though not elegance. Sue me.)
        i = 0

        # for each field entry in our guiDictionary (even blanks)
        for key in self.monDict:
            # make a shorter call to each individual value for brevity
            gui_type = self.monDict.get(key).get("type")
            gui_label = self.monDict.get(key).get("label")
            gui_color = self.monDict.get(key).get("color")
            gui_value = self.monDict.get(key).get("value")
            gui_units = self.monDict.get(key).get("units")
            gui_status = self.monDict.get(key).get("status")
            gui_format = self.monDict.get(key).get("format")

            # else, if the gui type is a "Header" or a "Blank" this is just text entry
            if gui_type in ["H", "B"]:
                j = 0
                self.monitor_widgets[i][j].config(text=" ")
                self.monitor_widgets[i][j] = tk.Label(self.root, text=gui_label, width=45)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=6)

            # else, if the gui type is the "Title" of the page, format as such
            elif gui_type in ['T']:
                j = 0
                self.monitor_widgets[i][j].config(text=" ")
                self.monitor_widgets[i][j] = tk.Label(self.root, text=gui_label, width=30)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=7, sticky=tk.W + tk.E)

            # else, if the gui type is a dialog, format as such
            elif gui_type in ['D']:
                j = 0
                self.monitor_widgets[i][j].config(text=" ")
                self.monitor_widgets[i][j] = tk.Label(self.root, text=gui_label, width=30)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=6, sticky=tk.W + tk.E)

            # status dialogs
            elif gui_type in ['S']:
                j = 0
                self.monitor_widgets[i][j].config(text=" ")
                value_string = "{label}".format(label = gui_label)
                self.monitor_widgets[i][j] = tk.Label(self.root, text=value_string, width=15)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=1)

                j = 2
                self.monitor_widgets[i][j].config(text=" ")
                value_string = "{value:.{format}f}{units}".format(format=gui_format, value=gui_value, units=gui_units)
                self.monitor_widgets[i][j] = tk.Label(self.root, text=value_string, width=10)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=1)

                j = 3
                self.monitor_widgets[i][j].config(text=" ")
                value_string = "{status}".format(status=gui_status)
                self.monitor_widgets[i][j] = tk.Label(self.root, text=value_string, width=15)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=1)

            # if we have a dynamic status message
            elif gui_type in ['DS']:
                j = 0
                self.monitor_widgets[i][j].config(text=" ")
                value_string = "{value}".format(value=gui_value)
                self.monitor_widgets[i][j] = tk.Label(self.root, text=value_string, width=45)
                self.monitor_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.monitor_widgets[i][j].grid(row=i, column=j, columnspan=7, rowspan=2)

            i = i + 1

        # everything is better with a puppy
        photo = self.pup1
        if self.pupper_counter % 3 == 0:
            photo = PhotoImage(file=r"pupper1_smol.png")
        elif self.pupper_counter % 3 == 1:
            photo = PhotoImage(file=r"pupper2_smol.png")
        elif self.pupper_counter % 3 == 2:
            photo = PhotoImage(file=r"pupper3_smol.png")

        photo_label = Label(image=photo, width=80, anchor=W)
        photo_label.grid(row=4, column=0)
        photo_label.image = photo

        photo_label = Label(image=photo, width=80, anchor=E)
        photo_label.grid(row=4, column=3)
        photo_label.image = photo

        self.pupper_counter = self.pupper_counter + 1

        if not self.programEnd:
            self.root.after(2000, self.monitor_update_screen)
        if self.programEnd:
            self.monitor_end_program()

    def setup_create(self):
        """ This definition creates the Ma'ii Experimental Setup Window and """

        try:
            #print("just killed root")
            self.root.destroy()
        except:
            #print("something bad happened with kill root")
            pass

        print("make new root")
        self.root = Tk()
        # Change the root title
        self.root.title("Ma\'ii Experimental Setup Wizard")

        # given the dictionary, we can define a widget list of placeholders
        gui_cols = range(len(next(iter(guiFields))))
        gui_rows = range(len(guiFields))
        self.setup_widgets = [[tk.Entry(self.root) for i in gui_cols] for j in gui_rows]

    def setup_update_screen(self):
        """ This definition controls display of GUI on the Ma'ii Experiment Setup page """

        self.setup_exp_compliance()
        self.setup_volt_compliance()
        self.setup_temp_compliance()
        self.setup_total_compliance()

        # the whole thing is effectively a loop... but each column/row may have different display parameters
        # in this event I split it apart for simplicity (though not elegance. Sue me.)
        i = 0

        # for each field entry in our guiDictionary (even blanks)
        for key in self.guiDict:
            # make a shorter call to each individual value for brevity
            gui_type = self.guiDict.get(key).get("type")
            gui_label = self.guiDict.get(key).get("label")
            gui_color = self.guiDict.get(key).get("color")
            gui_value = self.guiDict.get(key).get("value")
            gui_units = self.guiDict.get(key).get("units")
            gui_bounds = self.guiDict.get(key).get("bounds")
            gui_stats = self.guiDict.get(key).get("stats")

            # if the field is a "E" or "Entry" type
            if "E" in gui_type:

                # the first column is the label of the parameter
                j = 0
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_label, anchor=W, width=9)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j)

                # the second column is the current value + the units
                j = 1
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=str(gui_value)+gui_units, anchor=W, width=7)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j)

                # the third column is the entry field
                j = 2
                self.setup_widgets[i][j] = tk.Entry(self.root, width=10)
                self.setup_widgets[i][j].grid(row=i, column=j)

                # the fourth column is the range of allowed values
                j = 3
                if gui_type == "TE":
                    bound_txt = "("+str(gui_bounds[0])+" or "+str(gui_bounds[1])+")"
                else:
                    bound_txt = "("+str(gui_bounds[0])+" to "+str(gui_bounds[1])+gui_units+")"
                self.setup_widgets[i][j] = tk.Label(self.root, text=bound_txt, width=15)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color, anchor=W)
                self.setup_widgets[i][j].grid(row=i, column=j)

                # the fifth column is the button to accept the value
                j = 4
                ptFunc = partial(self.setup_get_input, self.setup_widgets[i][2], key)
                self.setup_widgets[i][j] = tk.Button(text=' Set '+gui_label.replace(':',''), command=ptFunc, width=15)
                self.setup_widgets[i][j].config(font=('arial', 10), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j)

                # the sixth column is a status box for the "validity" or not of the user's entry
                j = 5
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_stats, width=30)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j)

            # else, if the gui type is a "Header" or a "Blank" this is just text entry
            elif gui_type in ["H", "B"]:
                j = 0
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_label, width=30)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j, columnspan=6, sticky=tk.W + tk.E)

            # else, if the gui type is the "Title" of the page, format as such
            elif gui_type in ['T']:
                j = 0
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_label, width=30)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j, columnspan=7, sticky=tk.W + tk.E)

            # else, if the gui type is an inline text box, format as such
            elif gui_type in ['Tinline']:
                j = 0
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_label, width=70)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j, columnspan=6)

            # else, if the gui type is a dialog, format as such
            elif gui_type in ['D']:
                j = 0
                self.setup_widgets[i][j].config(text=" ")
                self.setup_widgets[i][j] = tk.Label(self.root, text=gui_label, width=30)
                self.setup_widgets[i][j].config(font=('arial', 12), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j, columnspan=6, sticky=tk.W + tk.E)

            # else if the gui type is a status text, format as such
            elif gui_type in ['S']:
                j = 0
                self.setup_widgets[i][j].config(text=" ")

                self.inCompliance = self.setup_total_compliance()
                if self.inCompliance:
                    bound_txt2 = "The current set of parameters is acceptable."
                    self.setup_widgets[i][j] = tk.Label(self.root, text=bound_txt2, width=60)
                    self.setup_widgets[i][j].config(font=('arial', 12), fg=self.dgr)
                    self.setup_widgets[i][j].grid(row=i, column=j, columnspan=6)
                elif not self.inCompliance:
                    bound_txt2 = "The current set of parameters is unacceptable. Please revise values."
                    self.setup_widgets[i][j] = tk.Label(self.root, text=bound_txt2, width=60)
                    self.setup_widgets[i][j].config(font=('arial', 12), fg=self.red)
                    self.setup_widgets[i][j].grid(row=i, column=j, columnspan=6)

            # else, if the gui type is a button only, format as such
            elif gui_type in ['BO']:
                j = 4
                ptFunc = partial(self.setup_continue_next, self.inCompliance)
                self.setup_widgets[i][j] = tk.Button(text="Continue", command=ptFunc, width=30)
                self.setup_widgets[i][j].config(font=('arial', 10), fg=gui_color)
                self.setup_widgets[i][j].grid(row=i, column=j)

            i = i + 1

        # we have a schematic which is to be displayed next to the user input... to help show graphically
        # what each parameter is doing.
        photo = PhotoImage(file=r"Schematic.png")
        photo_label = Label(image=photo, width=400)
        photo_label.grid(row=2, column=6, rowspan=len(guiFields), sticky=tk.W + tk.E)
        photo_label.image = photo

    def setup_construct_vtable(self):
        try:
            self.v_table = []

            v_max_ch1 = self.guiDict.get("V_CH1").get("value")
            v_max_ch2 = self.guiDict.get("V_CH2").get("value")
            voltage_steps = int(self.guiDict.get("V_steps").get("value"))
            type = self.guiDict.get("rzExp").get("value")

            print("the voltage tables are being constructed from:\n"
                  "V_CH1max: {vmax1}\n"
                  "V_CH2max: {vmax2}\n"
                  "Number steps: {steps}\n"
                  "exp type: {type}".format(vmax1=v_max_ch1,vmax2=v_max_ch2,steps=voltage_steps,type=type))

            total_range = abs(v_max_ch2) + abs(v_max_ch1)
            voltage_increment = round(total_range / voltage_steps, 1)
            print(voltage_increment)

            i_voltage = 0
            j_voltage = 0
            j = 0
            remainder = 0
            if type == "Tens.":
                for i in range(0, voltage_steps):
                    i_voltage = round(voltage_increment * (i), 1)
                    if i_voltage <= v_max_ch1:
                        self.v_table.append([i_voltage, 0])
                    if i_voltage > v_max_ch1:
                        if j == 0:
                            remainder = round(abs(i_voltage - v_max_ch1), 1)
                            self.v_table.append([v_max_ch1, -remainder])
                            j = j + 1
                        elif j != 0:
                            j_voltage = -(remainder + voltage_increment * j)
                            self.v_table.append([v_max_ch1, round(j_voltage)])
                            j = j + 1

                for volt in self.v_table:
                    if volt[0] > v_max_ch1 or volt[0] < 0:
                        print("shits fucked on v1")
                        raise VoltListError
                    if volt[1] > 0 or volt[1] < v_max_ch2:
                        print("shits fucked on v2")
                        raise VoltListError

                print(self.v_table)
                print(len(self.v_table))

            if type == "Comp.":
                for i in range(0, voltage_steps - 1):
                    i_voltage = round(voltage_increment * i, 1)
                    if i_voltage <= v_max_ch2:
                        self.v_table.append([0, i_voltage])
                    if i_voltage > v_max_ch2:
                        if j == 0:
                            remainder = round(abs(i_voltage - v_max_ch2), 1)
                            self.v_table.append([-remainder, v_max_ch2])
                        if j != 0:
                            j_voltage = -(remainder + voltage_increment * j)
                            self.v_table.append([round(j_voltage), v_max_ch2])
                        j = j + 1
                for volt in self.v_table:
                    if volt[0] < v_max_ch1 or volt[0] > 0:
                        print("shits fucked on v1")
                        raise VoltListError
                    if volt[1] < 0 or volt[1] > v_max_ch2:
                        print("shits fucked on v2")
                        raise VoltListError

                print(self.v_table)
                print(len(self.v_table))
        except VoltListError:
            print(self.v_table)
            print("WARNING: VOLTAGE LISTS NOT IN COMPLIANCE RANGE")
            self.voltListError = True

        volt_skip = int(self.guiDict.get("V_skip").get("value"))
        self.v_table = self.v_table[volt_skip:-1]

    def setup_continue_next(self, compliance):
        """
        This definition determines if we can move to the next phase... the monitor phase. The sole parameter
        is a boolean value evaluated earlier turing the setup_update_screen and it checks whether all user
        defined parameters are within acceptable bounds
        """

        v_max_ch1 = self.guiDict.get("V_CH1").get("value")
        v_max_ch2 = self.guiDict.get("V_CH2").get("value")
        voltage_steps = int(self.guiDict.get("V_steps").get("value"))
        type = self.guiDict.get("rzExp").get("value")

        # if compliance (through setup_total_compliance), we can move on the next phase... ask user again for sure
        if compliance:
            # construct voltage tables and print
            self.setup_construct_vtable()
            # if the user clicks yes, continue...
            if not self.voltListError and messagebox.askyesno(
                    "Parameters Accepted", "Would you like to continue to the measurement phase? \n "
                                           "Note: Please confirm the voltage table manually!!!\n\n"
                                           "Exp Type: {type}\n"
                                           "Max CH1 Allowed voltage: {max1}\n"
                                           "Max CH2 Allowed voltage: {max2}\n"
                                           "Number of steps allowed: {nsteps}\n"
                                           "Voltages [Ch1,Ch2]: {vlist}\n".format(max1=v_max_ch1, max2=v_max_ch2,
                                                                              nsteps=voltage_steps, type=type,
                                                                              vlist=self.v_table)):
                # destroy the current window
                self.root.destroy()
                # set control parameters to move onto next phase
                self.inDirectoryGet = True
                self.inExpSetup = False
                self.run()
            # if the user backs out
            else:
                # do nothing
                pass
        # if compliance fails, just show a error window and do not permit continuance
        else:
            print("I can\'t allow you to do that Jim...")
            messagebox.showerror("Illegal Variables Found", "Oh...\n I can\'t allow you to do that Jim...")

    def setup_get_input(self, field, key):
        """
        This definition controls how to retrieve input from a button, called during a button press
        via a partial() call. The parameters taken are the dictionary element key to set, and the
        button field, passed via a widget
        """

        # get the value stored in the entry box
        quarantined_var = field.get()

        # if the variable field type is a text entry:
        if self.guiDict.get(key).get("type") == "TE":
            # then we know we have to perform string matching... done here just through if..in
            # try to perform string operations in try...except
            try:
                quarantined_var = str(quarantined_var)
                # for each possible valid response
                for valid_string in self.guiDict.get(key).get("bounds"):
                    # check against our quarantined value... if it works, accept and set values... use green color
                    if quarantined_var == valid_string:
                        self.guiDict[key].update({"stats": 'User Value Accepted'})
                        self.guiDict[key].update({"value": quarantined_var})
                        self.guiDict[key].update({"color": self.dgr})
                        # special case, if the razorbill experiment type was altered, flag to invalidate voltages
                        if key == "rzExp":
                            self.voltModeChange = True
                        break
                # if we find no matches, raise a value error
                else:
                    raise ValueError

            # if we have a value error, just flag with a red color and chastise the user
            except ValueError:
                print('User input not understood')
                self.guiDict[key].update({"color": self.red})
                self.guiDict[key].update({"stats": 'User Value NRF... keeping previous'})

            # call to update the screen
            self.setup_update_screen()

        # otherwise... it's gotta be a numerical input
        else:
            # attempt to perform numerical operations
            try:
                if type(quarantined_var) is not int:
                    quarantined_var = round(float(quarantined_var), 1)
                # check whether the value falls within the necessary bounds, if so, accept and turn text green
                print(self.guiDict.get(key).get("bounds")[0])
                print(quarantined_var)
                print(self.guiDict.get(key).get("bounds")[1])
                print(self.guiDict.get(key).get("bounds")[0] >= quarantined_var)
                print(quarantined_var >= self.guiDict.get(key).get("bounds")[1])
                if self.guiDict.get(key).get("bounds")[0] >= quarantined_var >= self.guiDict.get(key).get("bounds")[1]:
                    self.guiDict[key].update({"stats": 'User Value Accepted'})
                    self.guiDict[key].update({"value": quarantined_var})
                    self.setup_chng_color(key, self.dgr)

                    # special case, if the user changed the temperature ranges
                    if key in ["F_max", "F_min"]:
                        # flag the temperature range change
                        self.tempChange = True
                    # if there is no temp range change, make sure to reset it back to false
                    else:
                        self.tempChange = False

                    # special case, if the value is meant to be an int
                    if key in ["V_steps"]:
                        quarantined_var = int(quarantined_var)
                        self.guiDict[key].update({"value": quarantined_var})

                # if things are out of range, raise a custom error, the RangeError
                else:
                    raise RangeError

            # For range error, chastise the user for out of range OOR values
            except RangeError:
                print('Out of range')
                self.guiDict[key].update({"color": self.red})
                self.guiDict[key].update({"stats": 'User Value OOR... keeping previous'})
            # For an incorrectly formatted response (e.g. dsfdjskl) chastise for not right form NRF
            except ValueError:
                print('Incorrect form')
                self.guiDict[key].update({"color": self.red})
                self.guiDict[key].update({"stats": 'User Value NRF... keeping previous'})

        # anytime user data is taken, even if incorrect, perform compliance checks for the experiment types
        # the voltage ranges, the temperature ranges, and the total compliance... don't forget to update screen!
        self.setup_exp_compliance()
        self.setup_volt_compliance()
        self.setup_temp_compliance()
        self.setup_total_compliance()
        self.setup_update_screen()

    def setup_chng_color(self, key, color):
        """ Arguably not needed, just a less annoying way to type out a color change """
        self.guiDict[key].update({"color":color})

    def setup_exp_compliance(self):
        """
        Definition that checks if the experiment types (e.g. the thermal profile hold/ramp) and the voltage
        experiment (e.g. tension/compression) have changed, and alters the parameters accordingly
        """

        # if the temperature experiment is a one-shot hold, then effectively disable the rate and T_min values
        if self.guiDict.get("d3TempExp") is not None and self.guiDict.get("d3TempExp").get("value") == "Ramp":
            self.setup_chng_color("T_max2", self.gry)
            self.guiDict["T_max2"].update({"stats": "Disabled due to exp. type"})
            self.guiDict["T_max2"].update({"value": self.guiDict.get("T_max2").get("bounds")[0]})
            self.setup_chng_color("T_min2", self.gry)
            self.guiDict["T_min2"].update({"stats": "Disabled due to exp. type"})
            self.guiDict["T_min2"].update({"value": self.guiDict.get("T_min2").get("bounds")[1]})
            self.setup_chng_color("T_rate2", self.gry)
            self.guiDict["T_rate2"].update({"stats": "Disabled due to exp. type"})
            self.guiDict["T_rate2"].update({"value": self.guiDict.get("T_rate2").get("bounds")[1]})
            self.tempExpWasMulti = True
        # if we return to a ramp-type, then return everything back to normal
        if self.guiDict.get("d3TempExp") is not None and self.guiDict.get("d3TempExp").get("value") == "Multi":
            if self.tempExpWasMulti is False:
                pass
            elif self.tempExpWasMulti is True:
                self.setup_chng_color("T_max2", self.blk)
                self.guiDict["T_max2"].update({"stats": "Holding Default Value"})
                self.guiDict["T_max2"].update({"value": self.guiDict.get("T_max2").get("bounds")[0]})
                self.setup_chng_color("T_min2", self.blk)
                self.guiDict["T_min2"].update({"stats": "Holding Default Value"})
                self.guiDict["T_min2"].update({"value": self.guiDict.get("T_min2").get("bounds")[1]})
                self.setup_chng_color("T_rate2", self.blk)
                self.guiDict["T_rate2"].update({"stats": "Holding Default Value"})
                self.guiDict["T_rate2"].update({"value": self.guiDict.get("T_rate2").get("bounds")[1]})
                self.tempExpWasMulti = False

        # if the voltage mode was changed, invalidate the voltages and force user to check
        if self.voltModeChange is True:
            self.voltModeChange = False
            self.guiDict["V_CH1"].update({"stats": "Force mode change, confirm voltage"})
            self.setup_chng_color("V_CH1", self.red)
            self.guiDict["V_CH2"].update({"stats": "Force mode change, confirm voltage"})
            self.setup_chng_color("V_CH2", self.red)

    def setup_volt_compliance(self):
        """
        Definition that checks for the voltage ranges to be within compliance ranges determined by Razorbill. As
        these values change with the temperature range, the voltage ranges are dynamically controlled by the
        program and are invalidated anytime a change is made to the temperatures. These functions were derived
        from the FC100 Razorbill manual.
        """

        # FOS is a factor of safety, set to 95%
        FoS = 0.95

        # these are the initial max/min ranges at 300K
        v_max_ch1 = 120
        v_min_ch2 = -20

        # get the max temperature from the guiDict
        #max_temp1 = float(self.guiDict.get("T_max").get("value"))
        #max_temp2 = float(self.guiDict.get("T_max2").get("value"))

        max_temp = float(self.guiDict.get("Temp").get("value"))
        print("max temp {t}".format(t=max_temp))

        # check the temperature against the different experimental ranges that are shown in the manual
        if 250 <= max_temp <= 300:
            v_max_ch1 = 120*FoS
            v_min_ch2 = -20*FoS
            print("T>250 active")
        elif 100 <= max_temp <= 250:
            v_max_ch1 = 120 * FoS
            v_min_ch2 = (-200 + 0.732*max_temp)*FoS
            print("100<T<250 active")
        elif 4 <= max_temp <= 100:
            v_max_ch1 = (200 - 0.833*max_temp)*FoS
            v_min_ch2 = (-200 + 0.732*max_temp)*FoS
            print("4<T<100 active")
        elif max_temp <= 4:
            print("<4 active")
            v_max_ch1 = 200*FoS
            v_min_ch2 = -200*FoS

        # we floor the values
        v_max_ch1 = math.floor(v_max_ch1)
        v_min_ch2 = math.floor(v_min_ch2)

        # if the experimental type is a tension experiment, then the CH1 ranges from 0-> positive
        # and the CH2 ranges from 0-> negative
        if self.guiDict.get("rzExp").get("value") == "Tens.":
            self.guiDict["V_CH1"].update({"bounds": [v_max_ch1, 0]})
            self.guiDict["V_CH2"].update({"bounds": [0, v_min_ch2]})
        # if the experimental type is a compression, then the values are reversed
        elif self.guiDict.get("rzExp").get("value") == "Comp.":
            self.guiDict["V_CH1"].update({"bounds": [0, v_min_ch2]})
            self.guiDict["V_CH2"].update({"bounds": [v_max_ch1, 0]})

        volt_steps = int(self.guiDict.get("V_steps").get("value"))
        self.guiDict["V_skip"].update({"bounds": [volt_steps, 0]})
        print([0, volt_steps])

    def setup_temp_compliance(self):
        """
        Definition that checks for temperature compliance. This means that the max and min temperatures
        are checked against each other, such that Max is always > Min (seems obvious eh...?)
        """

        # get the temperature limits from the guiDict
        max_temp = float(self.guiDict.get("Temp").get("value"))
        min_temp = float(self.guiDict.get("Temp").get("value"))
        max_field = float(self.guiDict.get("F_max").get("value"))
        min_field = float(self.guiDict.get("F_min").get("value"))


        # update the built in bounds using dictionary methods
        self.guiDict["F_max"].update({"bounds": [90000, min_field]})
        self.guiDict["F_min"].update({"bounds": [max_temp, -90000]})

        #field things
        #if max_temp == min_temp:
            #self.guiDict["T_max"].update({"stats": "Min/Max equal, use hold or change T"})
            #self.setup_chng_color("T_max", self.red)
            #self.guiDict["T_min"].update({"stats": "Min/Max equal, use hold or change T"})
            #self.setup_chng_color("T_min", self.red)

        # hash out
        # note that if the temperature change value is ever flagged true in this instance, invalidate voltages
        if self.tempChange is True:
            self.guiDict["V_CH1"].update({"stats": "Temp change detected, confirm voltage"})
            self.setup_chng_color("V_CH1", self.red)
            self.guiDict["V_CH2"].update({"stats": "Temp change detected, confirm voltage"})
            self.setup_chng_color("V_CH2", self.red)

        #switch to fields
        # update the built in bounds using dictionary methods
        #self.guiDict["T_max2"].update({"bounds": [300.0, min_temp2]})
        #self.guiDict["T_min2"].update({"bounds": [max_temp2, 1.8]})

        #hash out
        #if max_temp2 == min_temp2:
            #self.guiDict["T_max2"].update({"stats": "Min2/Max2 equal, use hold or change T"})
            #self.setup_chng_color("T_max2", self.red)
            #self.guiDict["T_min2"].update({"stats": "Min2/Max2 equal, use hold or change T"})
            #self.setup_chng_color("T_min2", self.red)

        #hash out
        # note that if the temperature change value is ever flagged true in this instance, invalidate voltages
        if self.tempChange is True:
            self.guiDict["V_CH1"].update({"stats": "Temp change detected, confirm voltage"})
            self.setup_chng_color("V_CH1", self.red)
            self.guiDict["V_CH2"].update({"stats": "Temp change detected, confirm voltage"})
            self.setup_chng_color("V_CH2", self.red)

    def setup_total_compliance(self):
        """
        This definition just checks if all the red is gone... literally. Yes, yes, more pythonic to have assigned
        a value to the dictionaries that holds "is valid" or whatever, but it's functionally identical and here
        I don't have to do anything extra.
        """

        #for each widget in the guiDict, check if the color is red... if so we've flagged it already
        for widj in self.guiDict:
            if self.guiDict[widj].get("color") == self.red:
                # return false... e.g NOT in compliance
                return False
        # if you made it through, return true... e.g. IN compliance
        return True

    def run(self):
        if self.inIntro:
            self.intro_create()
        elif self.inExpSetup:
            self.setup_create()
            self.setup_update_screen()
        elif self.inDirectoryGet:
            self.navigate_fileloc()
        elif self.inMonitor:
            self.monitor_create()
            self.monitor_update_screen()

        self.root.mainloop()


if __name__ == '__main__':
    RazorbillProgrammer().run()
