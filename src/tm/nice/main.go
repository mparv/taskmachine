package main

import (
	_ "nice/db_utils"
	"nice/fs_utils"
	"nice/processor"
	"fmt"
	"os"
	_ "math/rand"
	"net/http"
	"sync"
	_ "time"
	"encoding/json"
)

var fileMapping = make(map[int]fs_utils.FileInfo)
var TOTAL_VIDEOS = 0
var mutex sync.Mutex

type Video struct {
	Name string `json:"name"`
	Path string `json:"path"`
}

func getRandomVideoHandler(w http.ResponseWriter, r *http.Request) {
	mutex.Lock()
	defer mutex.Unlock()

 	response := map[string][]fs_utils.FileInfo{
 	    "video": {},
 	}

	for _, fileInfo := range fileMapping {
		response["video"] = append(response["video"], fileInfo)
	}

	w.Header().Set("Content-Type", "application/json")
	jsonData, err := json.Marshal(response)
	if err != nil {
			http.Error(w, "Error encoding response", http.StatusInternalServerError)
			return
	}
	_, err = w.Write(jsonData)
	if err != nil {
			http.Error(w, "Error writing response", http.StatusInternalServerError)
	}
}

func reloadVideosImpl() {
	TOTAL_VIDEOS = 0
	fileMapping = make(map[int]fs_utils.FileInfo)

	fmt.Println(os.Args)
	if len(os.Args) < 2 {
		fmt.Println("Usage: nice.exe <cfg-file>")
		os.Exit(1);
	}
	configPath := os.Args[1]

	locations, err := processor.ReadConfig(configPath)
	if err != nil {
		fmt.Println("Error:", err)
		os.Exit(1)
	}

	fmt.Println("File locations:", locations)

	for _, root := range locations {
		files, err := fs_utils.ListFiles(root)
		if err != nil {
			fmt.Println("Error:", err)
			return
		}

		for _, file := range files {
			//fmt.Printf("%+v\n", file.Filename)
			fileMapping[TOTAL_VIDEOS] = file
			TOTAL_VIDEOS += 1
		}
	}
}

func reloadVideos(w http.ResponseWriter, r *http.Request) {
	reloadVideosImpl()
}

func main() {
	// db_utils.Delete("general", "test", "basics")
	// db_utils.Create("general", "test", "basics", map[string]string{"new": "4"})
	// resp := db_utils.Read("general", "test", "basics")
	// fmt.Println(resp)
	// go func() {
	// 	for {
	// 		resp := db_utils.Read("pzk", "notes", "harbor-extension")
	// 		if resp == nil {
	// 			fmt.Println("Waiting to connect to TM app from harbor app")
	// 			time.Sleep(10 * time.Second)
	// 			continue
	// 		}
	// 		for _, values := range resp {
	// 			today := time.Now().Format("02-Jan-06")
	// 			db_utils.Create("pzk", "notes", "harbor-archived-" + today, values)
	// 		}
	// 		fmt.Println("Sleeping for 120 seconds for harbor-app")
	// 		time.Sleep(1200 * time.Second)

	// 		//db_utils.Delete("pzk", "notes", "harbor-extension")
	// 	}
	// }()

	http.HandleFunc("/getRandomVideo", getRandomVideoHandler)
	http.HandleFunc("/reloadVideos", reloadVideos)
	reloadVideosImpl()

	port := ":6666"
	fmt.Printf("Server is running on http://localhost%s\n", port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		fmt.Println("Error starting server:", err)
	}
}

