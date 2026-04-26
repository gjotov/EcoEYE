package main

import (
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"gocv.io/x/gocv"
)

type CameraStream struct {
	ID        string
	URL       string
	LastFrame gocv.Mat
	Mutex     sync.RWMutex
	Active    bool
}

// ВСЕ 9 КАМЕР
var cams = map[string]*CameraStream{
	// --- ЛЕНИНА ---
	"Lenina_36662": {URL: "https://flussonic2.powernet.com.ru:444/user36662/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Lenina_72349": {URL: "https://flussonic2.powernet.com.ru:444/user72349/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Lenina_82418": {URL: "https://flussonic2.powernet.com.ru:444/user82418/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},

	// --- МИРА ---
	"Mira_93635": {URL: "https://flussonic2.powernet.com.ru:444/user93635/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Mira_96368": {URL: "https://flussonic2.powernet.com.ru:444/user96368/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Mira_70484": {URL: "https://flussonic2.powernet.com.ru:444/user70484/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},

	// --- АЛЕКСАНДРОВА ---
	"Aleksandrova_12216":  {URL: "https://flussonic2.powernet.com.ru:444/user12216/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Aleksandrova_105259": {URL: "https://flussonic2.powernet.com.ru:444/user105259/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
	"Aleksandrova_12070":  {URL: "https://flussonic2.powernet.com.ru:444/user12070/tracks-v1/mono.m3u8?token=dont-panic-and-carry-a-towel"},
}

func main() {
	for id, cam := range cams {
		cam.ID = id
		cam.LastFrame = gocv.NewMat()
		cam.Active = false
		go captureLoop(cam)
	}

	http.HandleFunc("/frame", handleFrame)
	fmt.Println("🚀 Go Streamer: Загружено 9 камер. Порт :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func captureLoop(cam *CameraStream) {
	for {
		cap, err := gocv.OpenVideoCaptureWithAPI(cam.URL, gocv.VideoCaptureFFmpeg)
		if err != nil {
			fmt.Printf("[-] %s: Ретрай 5с...\n", cam.ID)
			time.Sleep(5 * time.Second)
			continue
		}

		img := gocv.NewMat()
		cam.Active = true
		fmt.Printf("[+] %s: ONLINE\n", cam.ID)

		for {
			if ok := cap.Read(&img); !ok {
				break
			}
			if img.Empty() {
				continue
			}

			cam.Mutex.Lock()
			img.CopyTo(&cam.LastFrame)
			cam.Mutex.Unlock()
			time.Sleep(20 * time.Millisecond) // 50 FPS лимит, чтобы не грузить проц зря
		}
		cam.Active = false
		cap.Close()
		img.Close()
		time.Sleep(2 * time.Second)
	}
}

func handleFrame(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	cam, ok := cams[id]
	if !ok {
		http.Error(w, "ID not found", 404)
		return
	}

	cam.Mutex.RLock()
	defer cam.Mutex.RUnlock()

	if !cam.Active || cam.LastFrame.Empty() {
		http.Error(w, "Wait...", 503)
		return
	}

	buf, _ := gocv.IMEncode(".jpg", cam.LastFrame)
	w.Header().Set("Content-Type", "image/jpeg")
	w.Write(buf.GetBytes())
}
