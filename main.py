import cv2 
import paho.mqtt.client as mqtt
import time

hueMax = 180
hueLow = 0
hueHigh = 17
satLow = 87
valueLow = 87


def on_trackbar(val):
    global hueLow
    global hueHigh
    global satLow
    global valueLow

    hueLow = cv2.getTrackbarPos("hueLow", 'CVImage')
    hueHigh = cv2.getTrackbarPos("hueHigh", 'CVImage')
    satLow = cv2.getTrackbarPos("satLow", 'CVImage')
    valueLow = cv2.getTrackbarPos("valueLow", 'CVImage')

def CarDetection(img):
    carIsPResent = 0
    hvs=cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype('uint8')
    carThreshold = cv2.inRange(hvs, (hueLow, satLow, valueLow), (hueHigh, 255, 255))
    _, redContours, _ = cv2.findContours(carThreshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in redContours:
        if cv2.arcLength(cnt, True) > 200.0:
            carIsPResent = 1
            approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt, True), True)
            cv2.drawContours(img, [approx], 0, (255), 5)
            x = approx.ravel()[0]
            y = approx.ravel()[1]

            cv2.putText(img, "Car", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0))
        else:
            pass
    cv2.putText(img, "CV done", (20, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0))
    return img, carThreshold, carIsPResent



if __name__ == "__main__":
    capture = cv2.VideoCapture('rtsp://192.168.1.4:8080/h264_ulaw.sdp')
    client = mqtt.Client()

    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_start()
    ttime = 0
    cv2.namedWindow('CVImage')
    cv2.createTrackbar("hueLow", 'CVImage' , 0, hueMax, on_trackbar)
    cv2.createTrackbar("hueHigh", 'CVImage' , 17, hueMax, on_trackbar)
    cv2.createTrackbar("satLow", 'CVImage' , 87, 255, on_trackbar)
    cv2.createTrackbar("valueLow", 'CVImage' , 87, 255, on_trackbar)
        
    while True:
        ret, frame = capture.read()
        cv2.imshow('Image', frame)
        cv2.waitKey(1)
        carImg, tImg, carIsPResent = CarDetection(frame)
        cv2.imshow('CVImage', carImg)
        cv2.waitKey(1)
        cv2.imshow('tempImg', tImg)
        cv2.waitKey(1)


        if time.time() - ttime > 1:
            ttime = time.time()
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            if carIsPResent:
                payload = current_time + ": Car is present, change lamp state!"
            else:
                payload = current_time + ": The road is free, RED LAMP!"
            client.publish("SzenzorHW/IPCamStreamer", payload)



