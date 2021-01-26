I started with basic cnn model with 32 filters input layer,and maxpooling layer of 2 * 2 pool size.
started with tanh activation function for input layer,but relu increased accuracy slightly.
adding a hidden layer with 64 nodes considerably increased the accuracy.
0.5 dropout rate
increasing number of nodes in hidden layer didint increase the performance considerably.
reducing number of filtrs in input layer reduced the training time,without affecting the accuracy.
Finally using softmax activation fuction for output layer instead of relu slightly increased the performnce.

