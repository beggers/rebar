package main

import (
	"fmt"
	"os"
	"regexp"
)

func main() {
	if len(os.Args) != 4 {
		fmt.Println("ERROR expected pattern and subject")
		return
	}
	source := os.Args[1]
	if os.Args[3] == "1" {
		source = "(?i)" + source
	}
	pattern, err := regexp.Compile(source)
	if err != nil {
		fmt.Println("ERROR", err)
		return
	}
	span := pattern.FindStringIndex(os.Args[2])
	if span == nil {
		fmt.Println("MISS")
		return
	}
	fmt.Printf("MATCH %d %d\n", span[0], span[1])
}
