package fs_utils

import (
	"crypto/md5"
	"encoding/hex"
	"io"
	"os"
	"path/filepath"
	"strconv"
)

type FileInfo struct {
	Filename string `json:"filename"`
	Filepath string `json:"filepath"`
	Filetype string `json:"filetype"`
	MD5Sum   string `json:"md5sum"`
	Size     string `json:"size"`
}

func GetFileMD5(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := md5.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func FormatFileSize(size int64) string {
	if size < 1024 {
		return strconv.FormatInt(size, 10) + "B"
	} else if size < 1024*1024 {
		return strconv.FormatFloat(float64(size)/1024, 'f', 1, 64) + "K"
	} else if size < 1024*1024*1024 {
		return strconv.FormatFloat(float64(size)/(1024*1024), 'f', 1, 64) + "M"
	}
	return strconv.FormatFloat(float64(size)/(1024*1024*1024), 'f', 1, 64) + "G"
}

func ListFiles(root string) ([]FileInfo, error) {
	var files []FileInfo

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() {
			md5sum, err := GetFileMD5(path)
			if err != nil {
				return err
			}

			ext := filepath.Ext(info.Name())
			if len(ext) > 0 {
				ext = ext[1:]
			}

			file := FileInfo{
				Filename: info.Name(),
				Filepath: path,
				Filetype: ext,
				MD5Sum:   md5sum,
				Size:     FormatFileSize(info.Size()),
			}
			files = append(files, file)
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return files, nil
}