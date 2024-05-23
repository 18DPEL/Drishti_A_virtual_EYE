import time
import cv2
import pygame
from gtts import gTTS
from transformers import pipeline, ViTImageProcessor
from gpiozero import Button, LED
import RPi.GPIO as GPIO
import multiprocessing

trigPin1 = 11
echoPin1 = 13
trigPin2 = 16
echoPin2 = 18
vibratorPin1 = 32
vibratorPin2 = 37

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(trigPin1, GPIO.OUT)
    GPIO.setup(trigPin2, GPIO.OUT)
    GPIO.setup(echoPin1, GPIO.IN)
    GPIO.setup(echoPin2, GPIO.IN)
    GPIO.setup(vibratorPin1, GPIO.OUT)
    GPIO.setup(vibratorPin2, GPIO.OUT)

def cleanup_gpio():
    GPIO.cleanup()

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

            if distance1 < 60:
                GPIO.output(vibratorPin1, GPIO.HIGH)
            else:
                GPIO.output(vibratorPin1, GPIO.LOW)

            if distance2 < 60:
                GPIO.output(vibratorPin2, GPIO.HIGH)
            else:
                GPIO.output(vibratorPin2, GPIO.LOW)

            time.sleep(0.5)

    except KeyboardInterrupt:
        GPIO.cleanup()

def image_processing_script(led, button, output_file):
    feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    drishti_aeye = pipeline("image-to-text", model="/home/drishti/Documents/Drishti/Save_vit_gpt_model", feature_extractor=feature_extractor)

    text = "Thank you for your patience. The entire system is now operational and ready to assist you."
    text_to_speech(text, output_file)

    while True:
        text = "DRISHTI is currently analyzing your front environment. Ensure the AI-enabled cap is properly connected and positioned."
        text_to_speech(text, output_file)

        img_path = "/home/drishti/Documents/Drishti/Images/image.jpg"
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        if ret:
            cv2.imwrite(img_path, frame)

        cap.release()
        cv2.destroyAllWindows()

        text = "AI analysis in progress. Front view information is being generated; it may take a few seconds. Your patience is appreciated."
        text_to_speech(text, output_file)

        gen_output = drishti_aeye(img_path)
        if gen_output:
            print(gen_output)
            sal = str(gen_output)
            sal = sal.split(':')
            text = sal[1]
            print(text)

            text_to_speech("DRISHTI predicts: In your front, " + str(text), output_file)

        text = "Ready to use one more time? Simply press the switch to start again."
        text_to_speech(text, output_file)

        while not button.is_pressed:
            time.sleep(0.1)

        led.toggle()
        text = "Thanks for choosing our innovative solution. We hope this experience was helpful to you."
        text_to_speech(text, output_file)

def main():
    setup_gpio()
    led = LED(22)
    button = Button(2)
    output_file = "output.mp3"
    text = "Welcome to DRISHTI AI, an innovative creation to assist blind persons in the light of AI."
    text_to_speech(text, output_file)

    text = "System initialization in progress. Please be patient; this may take a moment."
    text_to_speech(text, output_file)

    ultrasonic_process = multiprocessing.Process(target=ultrasonic_sensor_script)
    image_process = multiprocessing.Process(target=image_processing_script, args=(led, button, output_file))

    ultrasonic_process.start()
    image_process.start()

    ultrasonic_process.join()
    image_process.join()

    cleanup_gpio()

if __name__ == "__main__":
    main()
