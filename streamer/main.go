package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/go-zeromq/zmq4"
	"gocv.io/x/gocv"
)

type CameraStream struct {
	ID  string
	URL string
}

type FrameData struct {
	CamID string
	Bytes []byte
}

var cams = map[string]*CameraStream{
	"Lenina_36662":        {URL: "https://flussonic2.powernet.com.ru:444/user36662/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Lenina_72349":        {URL: "https://flussonic2.powernet.com.ru:444/user72349/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Lenina_82418":        {URL: "https://flussonic2.powernet.com.ru:444/user82418/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Mira_93635":          {URL: "https://flussonic2.powernet.com.ru:444/user93635/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Mira_96368":          {URL: "https://flussonic2.powernet.com.ru:444/user96368/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Mira_70484":          {URL: "https://flussonic2.powernet.com.ru:444/user70484/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Aleksandrova_12216":  {URL: "https://flussonic2.powernet.com.ru:444/user12216/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Aleksandrova_105259": {URL: "https://flussonic2.powernet.com.ru:444/user105259/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Aleksandrova_12070":  {URL: "https://flussonic2.powernet.com.ru:444/user12070/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
}

func main() {
	frameChan := make(chan FrameData, 100)

	// Start video capture loops
	for id, cam := range cams {
		cam.ID = id
		go captureLoop(cam, frameChan)
	}

	// Initialize Pure-Go ZMQ Publisher
	publisher := zmq4.NewPub(context.Background())
	defer publisher.Close()

	err := publisher.Listen("tcp://127.0.0.1:5555")
	if err != nil {
		log.Fatalf("ZMQ server start error: %v", err)
	}
	fmt.Println("🚀 Go Streamer (PURE GO): Broadcasting 9 cameras on ZMQ tcp://127.0.0.1:5555")

	for frame := range frameChan {
		msg := zmq4.NewMsgFrom(
			[]byte(frame.CamID),
			frame.Bytes,
		)

		err := publisher.Send(msg)
		if err != nil {
			log.Printf("[-] Error sending packet to ZMQ: %v", err)
		}
	}
}

func captureLoop(cam *CameraStream, frameChan chan<- FrameData) {
	for {
		cap, err := gocv.OpenVideoCaptureWithAPI(cam.URL, gocv.VideoCaptureFFmpeg)
		if err != nil {
			fmt.Printf("[-] %s: Connection error, retrying in 5s...\n", cam.ID)
			time.Sleep(5 * time.Second)
			continue
		}

		img := gocv.NewMat()
		fmt.Printf("[+] %s: CONNECTED\n", cam.ID)

		for {
			if ok := cap.Read(&img); !ok {
				break
			}
			if img.Empty() {
				continue
			}

			// Encode frame as JPEG (75% quality)
			buf, err := gocv.IMEncodeWithParams(gocv.JPEGFileExt, img, []int{gocv.IMWriteJpegQuality, 75})
			if err != nil {
				continue
			}

			frameChan <- FrameData{
				CamID: cam.ID,
				Bytes: buf.GetBytes(),
			}
			buf.Close()

			// Limit to 10 FPS
			time.Sleep(100 * time.Millisecond)
		}
		cap.Close()
		img.Close()
		fmt.Printf("[-] %s: Connection lost, reconnecting in 2s...\n", cam.ID)
		time.Sleep(2 * time.Second)
	}
}
