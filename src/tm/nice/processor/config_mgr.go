package processor

import (
        "fmt"
        "github.com/go-ini/ini"
        "strings"
)

func ReadConfig(configPath string) ([]string, error) {
        cfg, err := ini.Load(configPath)
        if err != nil {
                return nil, fmt.Errorf("failed to read config file: %v", err)
        }

        section, err := cfg.GetSection("nice")
        if err != nil {
                return nil, fmt.Errorf("missing [nice] section: %v", err)
        }

        key, err := section.GetKey("FILE_LOCATIONS")
        if err != nil {
                return nil, fmt.Errorf("missing FILE_LOCATIONS key: %v", err)
        }

        locations := strings.Split(key.String(), ",")
        return locations, nil
}