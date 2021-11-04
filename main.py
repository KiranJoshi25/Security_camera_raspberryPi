#all imports 
import RPi.GPIO as GPIO
import time
import os
from picamera  import PiCamera
from datetime import datetime
import boto3
from subprocess import call 
import threading
import json
lock = threading.Lock()


file = open("credentials.json")
var = json.load(file)
file.close()


Access_key_ID = var["Access_key_ID"]
Access_secret_key = var["Access_secret_key"]
Bucket_name = var["Bucket_name"]



class DoorSecurity():
    
    def current_date_time(self):
        self.now = datetime.now()
        return self.now.strftime("%m_%d_%Y_%H_%M_%S")
    
    
    def detect_motion_pir_sensor(self):
        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11,GPIO.IN)
        self.i = GPIO.input(11)
        GPIO.cleanup()
        return self.i
    
    def record_video(self):
        camera = PiCamera() 
        #camera.resolution = (640,480)
        camera.rotation = 180
        date_and_time = self.current_date_time()
        video_name = f'{date_and_time}.h264'
        camera.start_recording(video_name)
        
        #time.sleep(10)
        m = D.detect_motion_pir_sensor()
        while m!=0:
            m = D.detect_motion_pir_sensor()
            time.sleep(10)
            
        camera.stop_recording()
        print(f"motion detection and recording completed: {self.current_date_time()}")
        camera.close()
        self.convert_video_to_mp(video_name,date_and_time)
        
        os.remove(video_name)
    
    def convert_video_to_mp(self,video,date_and_time):
        command = "MP4Box -add " + video + " " + f'{date_and_time}.mp4'
        call([command], shell=True)
        #os.system('cls')
        self.upload_video_on_s3(f'{date_and_time}.mp4')
        
    def upload_video_on_s3(self,name):
        s3 = boto3.resource(
        service_name='s3',
        aws_access_key_id=Access_key_ID,
        aws_secret_access_key=Access_secret_key)
        s3.Bucket(Bucket_name).upload_file(name,name)
        print("Done")
        self.send_email(name)
        os.remove(name)
    
    def send_email(self,name):
        arn = var["arn"]
        snsClient = boto3.client('sns',
                                 aws_access_key_id = Access_key_ID,
                                 aws_secret_access_key = Access_secret_key,
                                 region_name = 'us-east-1'
        )
        publish_object = f"https://d2y5v6v5zq7590.cloudfront.net/{name}"
        response = snsClient.publish(TopicArn = arn,
                                 Message = publish_object,
                                 Subject  = "Motion Detected",
                                     #MessageAttributes = {}
                                )
     

        
    

global k
if __name__ == "__main__":
    
    D = DoorSecurity()

    while True:
        with lock:
            k = D.detect_motion_pir_sensor()
            if k == 1:
                print(f"{datetime.now()} Motion detected")
                D.record_video()
                print("Vdeo_recorded")
            else:
                print("No Motion Detected")
                time.sleep(1)
                
            
