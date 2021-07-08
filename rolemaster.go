package main

import (
	"context"
	"fmt"
)

func HandleRequest(ctx context.Context) (string, error) {
	return fmt.Sprintf("Hello world!"), nil
}

func main() {
	// lambda.Start(HandleRequest)
	fmt.Print("Hello world!")
}
