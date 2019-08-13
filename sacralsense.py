### WHAT DO YOU NEED TO RUN SACRALSENSE UI?

## You need a computer :)
## This computer can run on Mac, Linux, Raspbian OS!
## You might have some trouble with Windows though, so be careful :o

## You ALSO need minimum specs: 
##
## (These are Raspberry Pi based specs)
## CPU: 1.4GHz 64-bit quad-core processing
## GPU: Broadcom VideoCore IV
## RAM: 1GB 
## (in the future) Bluetooth: Bluetooth 4.1 Classic
## Storage: microSD
## GPIO: 40-pin header, populated
## Ports: HDMI, 3.5mm analogue audio-video jack, CSI, DSI

## You need the FOLLOWING software / libraries to run the below code:
##
## Python 3 (https://www.python.org)
## PySimpleGUI (https://pypi.org/project/PySimpleGUI/)
## (a) Scikit
## (b) NumPy
## (c) Matplotlib
## RPi.GPIO (can download from FSR code)
## Optionally, you can download a-c by just downloading Anaconda
## (https://www.anaconda.com/distribution)

## SAVE this .py file within PySimpleGUI directory :)
## You can run this file in terminal by doing: python3 sacralsense.py




import PySimpleGUI as sg
import os


# os.system('say "Welcome to sake rell sense"')
# For Linux based OS do
# os.system('spd-say "your program has finished"')
# May need to dl package, sudo apt install speech-dispatcher

### Functions are defined here, *outside* the while loop
## Pressure impedance fitting function
def ML_LinReg_p(my_weeks,my_ELOs,myslope=None,myavg=None):
	import math
	from sklearn import linear_model
	import numpy as np
	import matplotlib.pyplot as plt
	plt.style.use('seaborn-ticks')
	plt.rcParams["font.size"] = 14
    
# This does the fitting of the X and Y data
	my_out = np.polyfit(my_weeks,my_ELOs,1)
	slope = my_out[0]
	intercept = my_out[1]
    ## Now print equation based line for predictive purposes
    ## Also print("You are changing by", slope, "PU risk per day!")
	plt.plot(my_weeks,my_ELOs,'bo')
	plt.xlabel('Number of Days')
	plt.ylabel('Pressure Readings')
	plt.title('Pressure Readings Graph')
	axes = plt.gca()
	x_vals = np.array(axes.get_xlim())
	y_vals = intercept + slope*x_vals
	plt.plot(x_vals, y_vals, '--')
	plt.show()
	#sg.Popup('Sensor Trend Analysis', 'Patient Average Pressure: ' + str(math.ceil(sum(my_ELOs)/len(my_ELOs))))
	win7_active = True
	layout7 = [[sg.Text('Sensor Trend Analysis', size=(30, 1), font=("Helvetica", 25), text_color='black')],[sg.Text('Patient Average Pressure: ' + str(math.ceil(sum(my_ELOs)/len(my_ELOs))) , size=(30, 1), font=("Helvetica", 25), text_color='blue')]]
	win7 = sg.Window('Window 7').Layout(layout7)
	win7.Read()
	win7.Close()
	win7_active = False

	# if slope > 0:
	# 	print("The patient is gaining",math.ceil(slope),"pressure per day during this time frame")
	# if slope < 0:
	# 	print("The patient is losing",abs(math.ceil(slope)),"pressure per day during this time frame")
	# print("Patient average pressure during this time was: ",math.ceil(sum(my_ELOs)/len(my_ELOs)))

## Bioimpedance fitting function
def ML_LinReg_b(my_weeks,my_ELOs):
	import math
	from sklearn import linear_model
	import numpy as np
	import matplotlib.pyplot as plt
	plt.style.use('seaborn-ticks')
	plt.rcParams["font.size"] = 14
    
# This does the fitting of the X and Y data
	my_out = np.polyfit(my_weeks,my_ELOs,1)
	slope = my_out[0]
	intercept = my_out[1]
    ## Now print equation based line for predictive purposes
    ## Also print("You are changing by", slope, "PU risk per day!")
	plt.plot(my_weeks,my_ELOs,'bo')
	plt.xlabel('Number of Days')
	plt.ylabel('Bioimpedance')
	plt.title('Bioimpedance Readings Graph')
	axes = plt.gca()
	x_vals = np.array(axes.get_xlim())
	y_vals = intercept + slope*x_vals
	plt.plot(x_vals, y_vals, '--')
	plt.show()
	layout7 = [[sg.Text('Sensor Trend Analysis', size=(30, 1), font=("Helvetica", 25), text_color='black')],[sg.Text('Patient Average Bioimpedance: ' + str(math.ceil(sum(my_ELOs)/len(my_ELOs))) , size=(30, 1), font=("Helvetica", 25), text_color='blue')]]
	win7 = sg.Window('Window 7').Layout(layout7)
	win7.Read()
	win7_active = False
	# if slope > 0:
	# 	print("The patient has increased",math.ceil(slope),"bioimpedance per day during this time frame")
	# if slope < 0:
	# 	print("The patient has decreased",abs(math.ceil(slope)),"bioimpedance per day during this time frame")
	# print("Patient average bioimpedance during this time was: ",math.ceil(sum(my_ELOs)/len(my_ELOs)))

## Pressure sensor function for FSR
import time
def force():

    import time
    import os
    import RPi.GPIO as GPIO


    GPIO.setmode(GPIO.BCM)
    DEBUG = 1

    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(adcnum, clockpin, mosipin, misopin, cspin):
            if ((adcnum > 7) or (adcnum < 0)):
                    return -1
            GPIO.output(cspin, True)

            GPIO.output(clockpin, False)  # start clock low
            GPIO.output(cspin, False)     # bring CS low

            commandout = adcnum
            commandout |= 0x18  # start bit + single-ended bit
            commandout <<= 3    # we only need to send 5 bits here
            for i in range(5):
                    if (commandout & 0x80):
                            GPIO.output(mosipin, True)
                    else:
                            GPIO.output(mosipin, False)
                    commandout <<= 1
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)

            adcout = 0
            # read in one empty bit, one null bit and 10 ADC bits
            for i in range(12):
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)
                    adcout <<= 1
                    if (GPIO.input(misopin)):
                            adcout |= 0x1

            GPIO.output(cspin, True)
            
            adcout >>= 1       # first bit is 'null' so drop it
            return adcout

    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25
                                                                                                                                                                                                                                                                      
    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    # 10k trim pot connected to adc #0
    potentiometer_adc = 0;
    potentiometer_adc1 = 1;
    potentiometer_adc2 = 2;
    potentiometer_adc3 = 3;

    last_force = 0
    last_force1 = 0      # this keeps track of the last potentiometer value
    last_force2 = 0
    last_force3 = 0
    tolerance = 5       # to keep from being jittery we'll only change
                        # volume when the pot has moved more than 5 'counts'
    count = 0
    force_dif_average = 0
    force_dif_average1= 0
    force_dif_average2 = 0
    force_average = 0

    average_time = 1 #Averaging time in seconds

    while True:
            # we'll assume that the pot didn't move
            force_value_changed = False
            force_value_changed1 = False
            force_value_changed_ref = False

            # read the analog pins for each of the FSRs
            force_value = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
            force_value1 = readadc(potentiometer_adc1, SPICLK, SPIMOSI, SPIMISO, SPICS)
            force_value2 = readadc(potentiometer_adc2, SPICLK, SPIMOSI, SPIMISO, SPICS)
            force_value3 = readadc(potentiometer_adc3, SPICLK, SPIMOSI,  SPIMISO, SPICS)
            # how much has it changed since the last read?
            force_change = abs(force_value - last_force)
            ##force_change1 = abs(force_value1 - last_force1)
            ##force_change_ref = abs(force_value_ref - last_force_ref)
            
            # force difference between both sensors
            ##force_dif= force_value - force_value1
            ##force_dif_ref1 = force_value - force_value_ref
            ##force_dif_ref2 = force_value1 - force_value_ref
            
            
            #FOR TESTING
            

            ##if DEBUG:
                            #print ("force_change 1:", force_change)
             #       print ("last_force 1:", last_force)
            #print("Left Force Difference: ", abs(force_value-force_value3))
            #print("Center Force Difference: ", abs(force_value1-force_value3))
            #print("Right Force Difference: ", abs(force_value2-force_value3))
            left = abs(force_value - force_value3)
            center = abs(force_value1 - force_value3)
            right = abs(force_value2 - force_value3)
            return left, center, right
            
            #print ("force_value 1:", force_value)
    #        print ("force_value 2:", force_value1)
    #        print ("force_value 3: ", force_value2)
    #        print("force_value ref: ", force_value3)
                    #print ("force_change 2:", force_change1)
              #      print ("last_force 2:", last_force1)
               #     print ("Force_value_ref:", force_value_ref)

            if ( force_change > tolerance ):
                   force_value_changed = True
            ##if ( force_change1 > tolerance ):
              ##     force_value_changed1 = True
            ##if ( force_change_ref > tolerance ):
              ##     force_value_changed_ref = True

            #if DEBUG:
             #       print ("force_value_changed 1:", force_value_changed)
            #if DEBUG:
             #       print ("force_value_changed 2:", force_value_changed1)

            if ( force_value_changed ):
           #         set_volume = force_value / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
            #        set_volume = round(set_volume)          # round out decimal value
             #       set_volume = int(set_volume)            # cast volume as integer

              #      print ('Volume = {volume}%' .format(volume = set_volume))
               #     set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' .format(volume = set_volume)
                #    os.system(set_vol_cmd)  # set volume

         #           if DEBUG:
          #                  print ("set_volume", set_volume)
           #                 print ("tri_pot_changed", set_volume)

                    # save the potentiometer reading for the next loop
                    last_force = force_value

            ##if ( force_value_changed1 ):
               ## last_force1 = force_value1
            ##if ( force_value_changed_ref ):
              ##  last_force_ref = force_value_ref
                
            if count < average_time :
                count = count +1
                force_average = force_average + force_value
                ##force_dif_average = force_dif_average + force_dif
            ##force_dif_average1 = force_dif_average1 + force_dif_ref1
            ##force_dif_average2 = force_dif_average2 + force_dif_ref2
            else :
                force_dif_average = force_dif_average / average_time
                force_dif_average1 = force_dif_average1 / average_time
                force_dif_average2 = force_dif_average2 / average_time
                force_average = force_average / average_time
                #print ("Average: ", force_average)

                #print ("force_dif_average:" , force_dif_average)
                #print ("force_dif_average1:" , force_dif_average1)
                #print ("force_dif_average2:" , force_dif_average2)
                count = 0
                force_dif_average = 0
                force_dif_average1 = 0
                force_dif_average2 = 0
                force_average = 0
                force_value = 0

            # hang out and do nothing for one second
           
            time.sleep(4)
            
    lefts = []
    centers = []
    rights = []
    while True:
        leftx,centerx,rightx = force()
        lefts.append(leftx)
        centers.append(centerx)
        rights.append(rightx)
        print(lefts,centers,rights)
        time.sleep(4)

  ## Biompedance function         
def bioimped(readingperiod2):

    import time
    import os
    import RPi.GPIO as GPIO


    GPIO.setmode(GPIO.BCM)
    DEBUG = 1

    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(adcnum, clockpin, mosipin, misopin, cspin):
            if ((adcnum > 7) or (adcnum < 0)):
                    return -1
            GPIO.output(cspin, True)

            GPIO.output(clockpin, False)  # start clock low
            GPIO.output(cspin, False)     # bring CS low

            commandout = adcnum
            commandout |= 0x18  # start bit + single-ended bit
            commandout <<= 3    # we only need to send 5 bits here
            for i in range(5):
                    if (commandout & 0x80):
                            GPIO.output(mosipin, True)
                    else:
                            GPIO.output(mosipin, False)
                    commandout <<= 1
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)

            adcout = 0
            # read in one empty bit, one null bit and 10 ADC bits
            for i in range(12):
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)
                    adcout <<= 1
                    if (GPIO.input(misopin)):
                            adcout |= 0x1

            GPIO.output(cspin, True)
            
            adcout >>= 1       # first bit is 'null' so drop it
            return adcout

    # change these as desired - they're the pins connected from the
    # SPI port on the ADC to the Cobbler
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    # set up the SPI interface pins
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    # 10k trim pot connected to adc #0
    voltage_adc = 7


    last_voltage = 0      # this keeps track of the last voltage value
    tolerance = 5       # to keep from being jittery we'll only change
                        # volume when the pot has moved more than 5 'counts'
    count = 0
    voltage_dif_average = 0
    voltage_average = 0


    average_time = 30#Averaging time in seconds

    while True:
            # we'll assume that the pot didn't move
            voltage_value_changed = False
    #        force_value_changed1 = False
    #        force_value_changed_ref = False

            # read the analog pin
            voltage_value = readadc(voltage_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
            print ("value: ", voltage_value)
           
            voltage_change = abs(voltage_value - last_voltage)
           
            if ( voltage_change > tolerance ):
                   voltage_value_changed = True
            
            if ( voltage_value_changed ):
           
                    last_voltage = voltage_value
                          
            if count < average_time :
                count = count +1
                voltage_average = voltage_average + voltage_value
             
            else :
                voltage_dif_average = voltage_dif_average / average_time
                
                voltage_average = voltage_average / average_time
                print ("Average: ", voltage_average)
                return voltage_average
               
                count = 0
                voltage_dif_average = 0
                voltage_average = 0
                voltage_value = 0

            # hang out and do nothing for one second
            readingperiod2 = 1
            time.sleep(readingperiod2)

#############################################
## All functions defined above this line
#############################################

## THIS IS THE MAIN HOME SCREEN LAYOUT            
layout = [[ sg.Text('SacralSense', size=(30,1), font = ("Helvetica",70))],
#          [sg.Input(do_not_clear=True)],
 #        [sg.Text('', key='_OUTPUT_')],
          [sg.Button('Braden Risk Assessment',size=(30,7), font = ("Helvetica", 25)), sg.Button('Patient Information', size=(30,7),font = ("Helvetica", 25)), sg.Button('Current Sensor Readings', size=(30,7),font = ("Helvetica", 25))],[sg.Button('Sensor Trend Analysis', size=(30,7),font = ("Helvetica", 25)),sg.Button('Prevention Tools', size=(30,7),font = ("Helvetica", 25)), sg.Button('Treatments', size=(30,7),font = ("Helvetica", 25))],]

win1 = sg.Window('SacralSense').Layout(layout)

## INITIALIZES OTHER WINDOWS TO NOT BE OPEN AND ACT AS SWITCHES
win2_active=False
win3_active=False
win4_active=False
win5_active=False
win6_active=False
win7_active=False

## THIS IS CHECKING FOR USER TO SELECT A BUTTON
while True:
    ev1, vals1 = win1.Read(timeout=100)
    #win1.FindElement('_OUTPUT_').Update(vals1[0])
    if ev1 is None or ev1 == 'Exit':
        break
    
## Button, Braden Risk Assessment
    if ev1 == 'Braden Risk Assessment' and not win2_active:
        win2_active = True
        layout2 = [[sg.Text('Braden Scale Risk Assessment', size=(30, 1), font=("Helvetica", 25), text_color='black')],
                   [sg.Text('Sensory Perception: Ability to respond meaningfully to', size=(50, 1), font=("Helvetica", 10), text_color='black')
 ], [sg.Text('pressure-related discomfort',size=(50,1), font=("Helvetica",10), text_color='black')],
[sg.InputCombo(['1. COMPLETELY LIMITED', '2. VERY LIMITED', '3. SLIGHTLY LIMITED' , '4. NO IMPAIRMENT'], size=(50, 4))],      
 
 [sg.Text('Moisture: Degree to which skin is exposed to moisture', size=(100, 1), font=("Helvetica", 10), text_color='black')],
[sg.InputCombo(['1. CONSTANTLY MOIST', '2. OFTEN MOIST', '3. OCCASIONALLY MOIST' , '4. RARELY MOIST'], size=(50, 4))],
          
          [sg.Text('Activity: Degree of physical activity', size=(100, 1), font=("Helvetica", 10), text_color='black')],
[sg.InputCombo(['1. BEDFAST', '2. CHAIRFAST', '3. WALKS OCCASIONALLY' , '4. WALKS FREQUENTLY'], size=(50, 4))],
          
          [sg.Text('Mobility: Ability to change and control body position', size=(100, 1), font=("Helvetica", 10), text_color='black')],
[sg.InputCombo(['1. COMPLETELY INMOBILE', '2. VERY LIMITED', '3. SLIGHTLY LIMITED' , '4. NO LIMITATIONS'], size=(50, 4))],
          
          [sg.Text('Nutrition: Usual food intake pattern', size=(100, 1), font=("Helvetica", 10), text_color='black')],
[sg.InputCombo(['1. VERY POOR', '2. PROBABLY INADEQUATE', '3. ADEQUATE' , '4. EXCELLENT'], size=(50, 4))],
          
          [sg.Text('Friction and Shear', size=(100, 1), font=("Helvetica", 10), text_color='black')],
[sg.InputCombo(['1. PROBLEM', '2. POTENTIAL PROBLEM', '3. NO APPARENT PROBLEM'], size=(50, 4))], [sg.Submit(), sg.Cancel()]
,                   [sg.Button('Exit')]]
        win2 = sg.Window('Window 2').Layout(layout2)
        event, values  = win2.Read()


        #event, values  = sg.Window('Window 2', layout2, auto_size_text=True, default_element_size=(40, 1)).Read()
        print(values)
        if values == {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}:
            win2.Close()
            win2_active = False
        else:    
            print(values)
            result = int(values[0][0]) + int(values[1][0]) + int(values[2][0]) + int(values[3][0]) + int(values[4][0]) + int(values[5][0])
            
            if result <= 9:
                sg.Popup('Braden Scale Result:' + ' ' + str(result) + ' ' + 'SEVERE RISK', font = ("Helvetica", 25), text_color = 'red' )
                win2.Close()
                win2_active = False

            elif result > 9 and result <= 12:
                sg.Popup('Braden Scale Result:' + ' ' + str(result) + ' ' + 'HIGH RISK', font = ("Helvetica", 25), text_color = 'red' )
                win2.Close()
                win2_active = False

            elif result > 12 and result <= 14 :
                sg.Popup('Braden Scale Result:' + ' ' + str(result) + ' ' + 'MODERATE RISK', font = ("Helvetica", 25), text_color = 'red' )
                win2.Close()
                win2_active = False

            else:
                sg.Popup('Braden Scale Result:' + ' ' + str(result) + ' ' + 'MILD RISK', font = ("Helvetica", 25), text_color = 'red' )
                win2.Close()
                win2_active = False

            if event == 'Exit' or 'Cancel':
            	#win1 = sg.Window('SacralSense').Layout(layout)
            	win2_active = False
            	win1_active = True
            	continue

## Button, Patient Information Window
    if ev1 == 'Patient Information' and not win3_active:
        win3_active = True
        layout3 = [[sg.Text('Patient Information', size=(30, 1), font=("Helvetica", 25), text_color='black')],      
   [sg.Text('Name: '),
    sg.InputText()],

[sg.Text('Gender: '),
    sg.InputCombo(['Male', 'Female', 'Not specified'], size=(20, 3))],

[sg.Text('Age: '),
    sg.InputText()],

[sg.Text('Level of conciousness: '), sg.InputCombo(['Sedated', 'Non sedated'], size=(20, 3))],

[sg.Text('Existing pressure ulcers?: '),
    sg.InputCombo(['Yes', 'No'], size=(20, 3))], [sg.Text('Days in ICU: '),
    sg.InputText()],
    
    [sg.Text('Diet: '),
    sg.InputCombo(['Feeding tube', 'Liquid diet', 'Solid food'], size=(20, 3))],
    
    [sg.Text('Pre-existing conditions: ')],
    [sg.Checkbox('Anaemia', size=(15,1)), sg.Checkbox('Atrial fibrillation', size=(15,1)), sg.Checkbox ('COPD',size=(15,1)), sg.Checkbox ('Dehydration', size=(15,1)) ],
    [sg.Checkbox('Diabetes',size=(15,1)), sg.Checkbox ( 'Heart failure',size=(15,1)), sg.Checkbox ('Kidney disease',size=(15,1)), sg.Checkbox('Malnutrition',size=(15,1))],
    [sg.Checkbox('Peripheral vascular disease',size=(32,1)), sg.Checkbox('Sepsis', size=(15,1)), sg.Checkbox('Smoking', size=(15,1))],
    [sg.Checkbox('Spinal cord injury', size=(20,1)), sg.Checkbox('Other', size=(10,1)), sg.InputText()],[sg.Submit(), sg.Cancel()],[sg.Button('Exit')]]

        win3 = sg.Window('Window 3').Layout(layout3)
        event, values  = win3.Read()
        #event, values  = sg.Window('Patient Information', layout, auto_size_text=True, default_element_size=(40, 1)).Read()
        print(values)
        win3.Close()
        win3_active = False
        #event, values  = sg.Window('Window 2', layout2, auto_size_text=True, default_element_size=(40, 1)).Read()

## Button, Prevention Tools
    if ev1 == 'Prevention Tools' and not win3_active:
        win4_active = True
        layout4 = [[sg.Text('Prevention Tools', size=(30, 1), font=("Helvetica", 25), text_color='black')],
    
    [sg.Checkbox('SacralSense', font=("Helvetica", 15))],
    
    [sg.Checkbox('Heelift Boot', font=("Helvetica", 15))],
    [sg.Checkbox('Right foot',size=(15,1),text_color = 'blue'), sg.Checkbox('Left foot',size=(15,1),text_color = 'blue')],
    
    [sg.Checkbox('Hydrofoam Dressing', font=("Helvetica", 15))],
    [sg.Checkbox('Head',size=(15,1), text_color = 'blue'), sg.Checkbox('Right shoulder', size=(15,1),text_color = 'blue'), sg.Checkbox('Left shoulder',size=(15,1), text_color = 'blue'), sg.Checkbox('Right elbow',size=(15,1), text_color = 'blue'), sg.Checkbox('Left elbow', size=(15,1),text_color = 'blue')],
    [sg.Checkbox('Sacrum', size=(15,1), text_color = 'blue'), sg.Checkbox('Right heel', size=(15,1), text_color = 'blue'), sg.Checkbox('Left heel',size=(15,1),  text_color = 'blue')],

    [sg.Checkbox('Pillow', font=("Helvetica", 15))],
    [sg.Checkbox('Head',size=(15,1), text_color = 'blue'), sg.Checkbox('Right shoulder', size=(15,1),text_color = 'blue'), sg.Checkbox('Left shoulder',size=(15,1), text_color = 'blue'), sg.Checkbox('Right elbow',size=(15,1), text_color = 'blue'), sg.Checkbox('Left elbow', size=(15,1),text_color = 'blue')],
    [sg.Checkbox('Sacrum', size=(15,1), text_color = 'blue'), sg.Checkbox('Right heel', size=(15,1), text_color = 'blue'), sg.Checkbox('Left heel',size=(15,1),  text_color = 'blue')],[sg.Submit(), sg.Cancel()]]
        win4 = sg.Window('Window 4').Layout(layout4)
        event, values  = win4.Read()
        print(values)
        win4.Close()
        win4_active = False
 
## Button, Prevention Tools
    if ev1 == 'Treatments' and not win5_active:
        win5_active = True
        layout5 = [[sg.Text('Treatments', size=(30, 1), font=("Helvetica", 25), text_color='black')],

    [sg.Checkbox('Wound Dressing', font=("Helvetica", 15))],
    
    [sg.Checkbox('Head',size=(15,1), text_color = 'blue'), sg.Checkbox('Right shoulder', size=(15,1),text_color = 'blue'), sg.Checkbox('Left shoulder',size=(15,1), text_color = 'blue'), sg.Checkbox('Right elbow',size=(15,1), text_color = 'blue'), sg.Checkbox('Left elbow', size=(15,1),text_color = 'blue')],
    [sg.Checkbox('Sacrum', size=(15,1), text_color = 'blue'), sg.Checkbox('Right heel', size=(15,1), text_color = 'blue'), sg.Checkbox('Left heel',size=(15,1),  text_color = 'blue')],

    [sg.Checkbox('Negative Pressure Therapy', font=("Helvetica", 15))],

    [sg.Checkbox('Head',size=(15,1), text_color = 'blue'), sg.Checkbox('Right shoulder', size=(15,1),text_color = 'blue'), sg.Checkbox('Left shoulder',size=(15,1), text_color = 'blue'), sg.Checkbox('Right elbow',size=(15,1), text_color = 'blue'), sg.Checkbox('Left elbow', size=(15,1),text_color = 'blue')],
    [sg.Checkbox('Sacrum', size=(15,1), text_color = 'blue'), sg.Checkbox('Right heel', size=(15,1), text_color = 'blue'), sg.Checkbox('Left heel',size=(15,1),  text_color = 'blue')],

    [sg.Checkbox('Medication', font=("Helvetica", 15))],

    [sg.Checkbox('Nonsteroidal anti-inflammatory drugs',size=(35,1), text_color = 'blue'), sg.Checkbox('Topical pain medications',size=(27,1), text_color = 'blue'), sg.Checkbox('Topical Antibiotics',size=(27,1), text_color = 'blue'), sg.Checkbox('Oral Antibiotics',size=(27,1), text_color = 'blue')],

    [sg.Checkbox('Reconstructive Surgery', font=("Helvetica", 15))],

    [sg.Checkbox('Head',size=(15,1), text_color = 'blue'), sg.Checkbox('Right shoulder', size=(15,1),text_color = 'blue'), sg.Checkbox('Left shoulder',size=(15,1), text_color = 'blue'), sg.Checkbox('Right elbow',size=(15,1), text_color = 'blue'), sg.Checkbox('Left elbow', size=(15,1),text_color = 'blue')],
    [sg.Checkbox('Sacrum', size=(15,1), text_color = 'blue'), sg.Checkbox('Right heel', size=(15,1), text_color = 'blue'), sg.Checkbox('Left heel',size=(15,1),  text_color = 'blue')],

[sg.Submit(), sg.Cancel()],[sg.Button('Exit')]]        
        win5 = sg.Window('Window 5').Layout(layout5)
        event, values  = win5.Read()
        print(values)
        win5.Close()
        win5_active = False
        
## Button, Current Sensor Readings
    if ev1 == 'Current Sensor Readings' and not win6_active:
        win6_active = True
        testval_p = 339
        testval_b = 913
        if testval_p < 800 and 1000<testval_b<100000:
        	ss_says = 'Patient is doing well!'
        elif testval_p < 800 and testval_b < 1000:
        	ss_says = 'Patient is at risk!'
        	#os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        #os.system('say "Warning! Patient is at risk"')
        layout6 = [[sg.Text('Current Sensor Readings', size=(30, 3), font=("Helvetica", 25), text_color='black')], [sg.Text('Left Pressure Reading: ' + str(testval_p), size=(30, 3), font=("Helvetica", 25), text_color='black')],[sg.Text('Center Pressure Reading: ' + str(573), size=(30, 3), font=("Helvetica", 25), text_color='black')],[sg.Text('Right Pressure Reading: ' + str(892), size=(30, 3), font=("Helvetica", 25), text_color='orange')],[sg.Text('Bioimpedance Reading: ' + str(testval_b), size=(30, 3), font=("Helvetica", 25), text_color='orange')], [sg.Text(ss_says, size=(30, 3), font=("Helvetica", 25), text_color='red')],[sg.Button('Calibrate',size = (30,3), font = ("Helvetica",18))]]
        
        win6 = sg.Window('Window 6').Layout(layout6)
        event, values = win6.Read()
        # Put this warning for values outside thresholds
        
        win6_active = False
        #force(1)
        #bioimped(1)
        
## Button, Sensor Trend Analysis
    if ev1 == 'Sensor Trend Analysis' and not win7_active:
        #win7_active = True
        #layout7 = [[sg.Text('Sensor Trend Analysis', size=(30, 1), font=("Helvetica", 25), text_color='black')]]
        testdays = [1,2,3,4,5,6,7,8,9,10]
        testvals_p = [300,350,400,500,650,800,840,870,900,950]
        testvals_b = [5000,4000,3500,3300,2900,2600,2300,2000,1500,900]
        #layout7 = [[sg.Text('Sensor Trend Analysis', size=(30, 1), font=("Helvetica", 25), text_color='black')]]
        ML_LinReg_p(testdays,testvals_p)
        ML_LinReg_b(testdays,testvals_b)
        # The above ML_LinReg functions call upon functions defined
        # at the beginning of this code
        #win7 = sg.Window('Window 7').Layout(layout7)
        #win7.Read()
        #win7_active = False
        


