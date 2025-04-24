package db_utils

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
)

const (
	CREATE_API_URL = "https://localhost:5000/internal/universe/create" 
	READ_API_URL = "https://localhost:5000/internal/universe/read" 
	DELETE_API_URL = "https://localhost:5000/internal/universe/delete" 
	BEARER_TOKEN = "16-Nov-24"
)

func Create(tenant string, database string, table string, dataObject map[string]string) {

	payload := map[string]interface{}{
		"dataObject": dataObject,
		"tenant":     tenant,
		"database":   database,
		"table":      table,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Error marshaling JSON: %v", err)
	}

	req, err := http.NewRequest("POST", CREATE_API_URL, bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Error creating request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Bearer-Token", BEARER_TOKEN)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error making request: %v", err)
		return
	}
	defer resp.Body.Close()

	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading response body: %v", err)
	}
}

func Read(tenant string, database string, table string) []map[string]string {
	payload := map[string]string{
		"tenant":     tenant,
		"database":   database,
		"table":      table,
	}
	jsonData, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Error marshaling JSON: %v", err)
	}

	req, err := http.NewRequest("POST", READ_API_URL, bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Error creating request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Bearer-Token", BEARER_TOKEN)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error making request: %v", err)
		return nil
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading response body: %v", err)
	}

	var result []map[string]string
	err = json.Unmarshal(body, &result)
	if err != nil {
		log.Printf("Error unmarshaling JSON: %v", err)
	}

	return result
}

func Delete(tenant string, database string, table string) {

	payload := map[string]string{
		"tenant":     tenant,
		"database":   database,
		"table":      table,
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Error marshaling JSON: %v", err)
	}

	req, err := http.NewRequest("POST", DELETE_API_URL, bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("Error creating request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Bearer-Token", BEARER_TOKEN)

	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Transport: tr}

	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error making request: %v", err)
	}
	defer resp.Body.Close()

	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading response body: %v", err)
	}
}