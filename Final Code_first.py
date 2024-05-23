import os
import time
import cv2
import pygame
from gtts import gTTS
from transformers import pipeline
from gpiozero import Button, LED
#from picamera2 import Picamera2
import RPi.GPIO as GPIO
import multiprocessing



def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_file)
    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.quit()
    os.remove(output_file)

# Define the pins for the ultrasonic sensors
trigPin1 = 11
echoPin1 = 13
trigPin2 = 16
echoPin2 = 18
vibratorPin1 = 32
vibratorPin2 = 37

# Set up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(trigPin1, GPIO.OUT)
GPIO.setup(trigPin2, GPIO.OUT)
GPIO.setup(echoPin1, GPIO.IN)
GPIO.setup(echoPin2, GPIO.IN)
GPIO.setup(vibratorPin1, GPIO.OUT)
GPIO.setup(vibratorPin2, GPIO.OUT)
GPIO.setwarnings(False)



# Wellcome message
#print("hello, we are Team DRISHTI_EYE, Thanks for using our product")
#print("Wait a sec, our AI Model is loading.......")
text = "Hello, we are Team DRISHTI, Thanks for using our innovation, our AI Model is loading. It may take some time,please hold your patience."
output_file = "output.mp3"
text_to_speech(text, output_file)
def getDistance(trigPin, echoPin):
    GPIO.output(trigPin, GPIO.LOW)
    time.sleep(0.000002)
    
    GPIO.output(trigPin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigPin, GPIO.LOW)
    
    while GPIO.input(echoPin) == 0:
        pulse_start = time.time()
    
    while GPIO.input(echoPin) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2.0  # Speed of sound is 34300 cm/s
    return distance

def ultrasonic_sensor_script():
   try:
       while True:
           distance1 = getDistance(trigPin1, echoPin1)
           distance2 = getDistance(trigPin2, echoPin2)

           print("Distance 1: {:.2f} cm".format(distance1))
           print("Distance 2: {:.2f} cm".format(distance2))

           if distance1 < 30:
               GPIO.output(vibratorPin1, GPIO.HIGH)
           else:
               GPIO.output(vibratorPin1, GPIO.LOW)

           if distance2 < 30:
               GPIO.output(vibratorPin2, GPIO.HIGH)
           else:
               GPIO.output(vibratorPin2, GPIO.LOW)

           time.sleep(0.5)

   except KeyboardInterrupt:
       GPIO.cleanup()


def image_processing_script():
    led = LED(22)
    button = Button(2)
    
    # Getting the pipeline model
    Drishti_AEYE = pipeline("image-to-text", model="/home/drishti/Documents/Drishti/Saved_Model")
    #print("Loading Done")
    text = "Thanks for your patience...Drishti is ready assist you"
    output_file = "output.mp3"
    text_to_speech(text, output_file)
    
    user_input = 0
    while True:
        # Taking the images and then supplying it to the model for prediction
        #print("AI is looking in front of you, please hold the AI Camera......")
        text = "Drishti is looking, please hold the AI Camera."
        text_to_speech(text, output_file)
        '''
        picam2 = Picamera2()
        picam2.start_preview()
        #config = picam2.create_still_configuration({"size": (640, 480)})
        img=picam2.capture_still()
        img_path = "/home/drishti/Documents/Drishti/Images/testresize.jpg"
        #picam2.start_and_capture_file(img_path, capture_mode=config)
        img.save(img_path)
        picam2.stop_preview()
        #picam2.close()
        print("Done")'''
        img_path = "/home/drishti/Documents/Drishti/Images/image.jpg"
        cap=cv2.VideoCapture(0)
        ret,frame=cap.read()
        if ret:
            cv2.imwrite(img_path,frame)
        cap.release()
        cv2.destroyAllWindows() 
            
        # Generating the text from the captured image
        #print("Generating your front view information,.......")
        #print("so please wait for us")
        text = "Drishti,generating your front view information,please hold your patience again."
        text_to_speech(text, output_file)
        
        gen_output = Drishti_AEYE(img_path)
        #print(gen_output)
        sal = str(gen_output)
        sal = sal.split(':')
        #print(sal[1])
        text = sal[1]
        text = "Drishti saying..."
        text_to_speech(text, output_file)
        text_to_speech(str(text), output_file)
        text = "To use one more time, please press the switch."
        print(text)
        text_to_speech(str(text), output_file)
        button.wait_for_press()
        led.toggle()
        text="Drishti is thanking you,hope this helped you"
        text_to_speech(text, output_file)



    # Create two separate processes for the two scripts
ultrasonic_process = multiprocessing.Process(target=ultrasonic_sensor_script)
image_process = multiprocessing.Process(target=image_processing_script)
    
    # Start both processes
ultrasonic_process.start()
image_process.start()
    
    # Wait for both processes to finish
ultrasonic_process.join()
image_process.join()
