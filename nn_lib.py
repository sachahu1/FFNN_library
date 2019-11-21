import numpy as np
import pickle

def xavier_init(size, gain=1.0):
    """
    Xavier initialization of network weights.
    """
    low = -gain * np.sqrt(6.0 / np.sum(size))
    high = gain * np.sqrt(6.0 / np.sum(size))
    return np.random.uniform(low=low, high=high, size=size)


class Layer:
    """
    Abstract layer class.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def forward(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def backward(self, *args, **kwargs):
        raise NotImplementedError()

    def update_params(self, *args, **kwargs):
        pass


class MSELossLayer(Layer):
    """
    MSELossLayer: Computes mean-squared error between y_pred and y_target.
    """

    def __init__(self):
        self._cache_current = None

    @staticmethod
    def _mse(y_pred, y_target):
        return np.mean((y_pred - y_target) ** 2)

    @staticmethod
    def _mse_grad(y_pred, y_target):
        return 2 * (y_pred - y_target) / len(y_pred)

    def forward(self, y_pred, y_target):
        self._cache_current = y_pred, y_target
        return self._mse(y_pred, y_target)

    def backward(self):
        return self._mse_grad(*self._cache_current)


class CrossEntropyLossLayer(Layer):
    """
    CrossEntropyLossLayer: Computes the softmax followed by the negative log-
    likelihood loss.
    """

    def __init__(self):
        self._cache_current = None

    @staticmethod
    def softmax(x):
        numer = np.exp(x - x.max(axis=1, keepdims=True))
        denom = numer.sum(axis=1, keepdims=True)
        return numer / denom

    def forward(self, inputs, y_target):
        assert len(inputs) == len(y_target)
        n_obs = len(y_target)
        probs = self.softmax(inputs)
        self._cache_current = y_target, probs

        out = -1 / n_obs * np.sum(y_target * np.log(probs))
        return out

    def backward(self):
        y_target, probs = self._cache_current
        n_obs = len(y_target)
        return -1 / n_obs * (y_target - probs)


class SigmoidLayer(Layer):
    """
    SigmoidLayer: Applies sigmoid function elementwise.
    """

    def __init__(self):
        self._cache_current = None
        self.f_prime = 0

    def forward(self, x):
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        self._cache_current = 1/(1 + np.exp(-x))

        return self._cache_current
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def backward(self, grad_z):
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        self.f_prime = np.multiply(self._cache_current, np.ones_like(self._cache_current)-self._cache_current)
        grad_loss_wrt_inputs = np.multiply(grad_z, self.f_prime)

        return(grad_loss_wrt_inputs)

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


class ReluLayer(Layer):
    """
    ReluLayer: Applies Relu function elementwise.
    """

    def __init__(self):
        self._cache_current = None

    def forward(self, x):

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        self._cache_current = np.maximum(np.zeros_like(x), x)
        #self._cache_current = self.z
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

        return self._cache_current

    def backward(self, grad_z):
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        self.f_prime = self._cache_current.copy()
        self.f_prime[self.f_prime<0] = 0
        self.f_prime[self.f_prime>0] = 1

        grad_loss_wrt_inputs = np.multiply(grad_z, self.f_prime) # GRAD_Z for linear unit
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

        return(grad_loss_wrt_inputs)


class LinearLayer(Layer):
    """
    LinearLayer: Performs affine transformation of input.
    """

    def __init__(self, n_in, n_out):
        """Constructor.

        Arguments:
            n_in {int} -- Number (or dimension) of inputs.
            n_out {int} -- Number (or dimension) of outputs.
        """
        self.n_in = n_in
        self.n_out = n_out

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        self._W = np.reshape(xavier_init((self.n_in * self.n_out)), (self.n_in, self.n_out))
        self._b = np.reshape(np.random.randn((self.n_out)), (1, self.n_out))

        self._cache_current = None
        self._grad_W_current = None
        self._grad_b_current = None

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def forward(self, x):
        """
        Performs forward pass through the layer (i.e. returns Wx + b).

        Logs information needed to compute gradient at a later stage in
        `_cache_current`.

        Arguments:
            x {np.ndarray} -- Input array of shape (batch_size, n_in).

        Returns:
            {np.ndarray} -- Output array of shape (batch_size, n_out)
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        self.batch_size = x.shape[0]
        self._cache_current = x

        # STORE CACHE FOR BACKWARD PROP
        #temp_Z = (np.matmul(x, self._W) + self._b)
        #self._cache_current  = [temp_Z, self._W]
        return (np.matmul(x, self._W) + self._b)

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def backward(self, grad_z):
        """
        Given `grad_z`, the gradient of some scalar (e.g. loss) with respect to
        the output of this layer, performs back pass through the layer (i.e.
        computes gradients of loss with respect to parameters of layer and
        inputs of layer).

        Arguments:
            grad_z {np.ndarray} -- Gradient array of shape (batch_size, n_out).

        Returns:
            {np.ndarray} -- Array containing gradient with repect to layer
                input, of shape (batch_size, n_in).
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        x = self._cache_current

        self._grad_W_current = np.matmul(x.T, grad_z)
        self._grad_b_current = np.matmul(np.ones((1, self.batch_size)), grad_z)

        grad_loss_wrt_inputs = np.matmul(grad_z, self._W.T)

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

        return(grad_loss_wrt_inputs)

    def update_params(self, learning_rate):
        """
        Performs one step of gradient descent with given learning rate on the
        layer's parameters using currently stored gradients.

        Arguments:
            learning_rate {float} -- Learning rate of update step.
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        self._W -= learning_rate*self._grad_W_current
        self._b -= learning_rate*self._grad_b_current

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

class MultiLayerNetwork(object):
    """
    MultiLayerNetwork: A network consisting of stacked linear layers and
    activation functions.
    """

    def __init__(self, input_dim, neurons, activations):
        """Constructor.

        Arguments:
            input_dim {int} -- Dimension of input (excluding batch dimension).
            neurons {list} -- Number of neurons in each layer represented as a
                list (the length of the list determines the number of layers).
            activations {list} -- List of the activation function to use for
                each layer.
        """
        self.input_dim = input_dim # D
        self.neurons = neurons # L
        self.activations = activations # L

        self._layers = [None]*len(self.neurons)
        self._w_gradients = [None]*len(self.neurons)
        self._b_gradients = [None]*len(self.neurons)
        self.feature_list = [self.input_dim] + self.neurons

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        for index, feature in enumerate(self.neurons):
            self._layers[index] = [LinearLayer(self.feature_list[index],self.feature_list[index+1]),
                                    self.find_activation_func(index)]

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def find_activation_func(self,index):
        if self.activations[index] == "relu":
            activation_class = ReluLayer()
        elif self.activations[index] == "linear":
            activation_class = LinearLayer()
        elif self.activations[index] == "sigmoid":
            activation_class = SigmoidLayer()
        else:
            raise AssertionError("Wrong activation function")
        return activation_class

    def forward(self, x):
        """
        Performs forward pass through the network.

        Arguments:
            x {np.ndarray} -- Input array of shape (batch_size, input_dim).

        Returns:
            {np.ndarray} -- Output array of shape (batch_size,
                #_neurons_in_final_layer)
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        for i in range(len(self.neurons)):
            x = self._layers[i][1].forward(self._layers[i][0].forward(x))
        return x

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def __call__(self, x):
        """
        Method to call the forward class from MultiLayer
        """
        return self.forward(x)

    def backward(self, grad_z):
        """
        Performs backward pass through the network.

        Arguments:
            grad_z {np.ndarray} -- Gradient array of shape (1,
                #_neurons_in_final_layer).

        Returns:
            {np.ndarray} -- Array containing gradient with repect to layer
                input, of shape (batch_size, input_dim).
        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        for layer_n in range(len(self.neurons)-1,-1,-1):
            grad_z = self._layers[layer_n][0].backward(self._layers[layer_n][1].backward(grad_z))
        return grad_z #RETURNS GRADIENT OF FUNC WRT TO INPUTS

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def update_params(self, learning_rate):
        """
        Performs one step of gradient descent with given learning rate on the
        parameters of all layers using currently stored gradients.

        Arguments:
            learning_rate {float} -- Learning rate of update step.
        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        for layer_n in range(len(self.neurons)-1,-1,-1):
            self._layers[layer_n][0].update_params(learning_rate)
        return 0 #RETURNS GRADIENT OF FUNC WRT TO INPUTS
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


def save_network(network, fpath):
    """
    Utility function to pickle `network` at file path `fpath`.
    """
    with open(fpath, "wb") as f:
        pickle.dump(network, f)


def load_network(fpath):
    """
    Utility function to load network found at file path `fpath`.
    """
    with open(fpath, "rb") as f:
        network = pickle.load(f)
    return network


class Trainer(object):
    """
    Trainer: Object that manages the training of a neural network.
    """

    def __init__(
        self,
        network,
        batch_size,
        nb_epoch,
        learning_rate,
        loss_fun,
        shuffle_flag
    ):
        """Constructor.

        Arguments:
            network {MultiLayerNetwork} -- MultiLayerNetwork to be trained.
            batch_size {int} -- Training batch size.
            nb_epoch {int} -- Number of training epochs.
            learning_rate {float} -- SGD learning rate to be used in training.
            loss_fun {str} -- Loss function to be used. Possible values: mse,
                bce.
            shuffle_flag {bool} -- If True, training data is shuffled before
                training.
        """
        self.multilayer_network = network
        self.batch_size = batch_size
        self.nb_epoch = nb_epoch
        self.learning_rate = learning_rate
        self.loss_fun = loss_fun
        self.shuffle_flag = shuffle_flag

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        if self.loss_fun is 'mse':
            self._loss_layer = MSELossLayer()
        elif self.loss_fun is 'softmax_cross_entropy':
            self._loss_layer = CrossEntropyLossLayer()
        else:
            raise Exception('Wrong Loss, chose between: mse, softmax_cross_entropy')

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    @staticmethod
    def shuffle(input_dataset, target_dataset):
        """
        Returns shuffled versions of the inputs.

        Arguments:
            - input_dataset {np.ndarray} -- Array of input features, of shape
                (#_data_points, n_features).
            - target_dataset {np.ndarray} -- Array of corresponding targets, of
                shape (#_data_points, ).

        Returns: 2-tuple of np.ndarray: (shuffled inputs, shuffled_targets).
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        stacked_data = np.hstack((input_dataset,target_dataset))
        np.random.shuffle(stacked_data)
        return stacked_data[:,:-target_dataset.shape[1]], stacked_data[:,-target_dataset.shape[1]:]
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def train(self, input_dataset, target_dataset):
        """
        Main training loop. Performs the following steps `nb_epoch` times:
            - Shuffles the input data (if `shuffle` is True)
            - Splits the dataset into batches of size `batch_size`.
            - For each batch:
                - Performs forward pass through the network given the current
                batch of inputs.
                - Computes loss.
                - Performs backward pass to compute gradients of loss with
                respect to parameters of network.
                - Performs one step of gradient descent on the network
                parameters.

        Arguments:
            - input_dataset {np.ndarray} -- Array of input features, of shape
                (#_training_data_points, n_features).
            - target_dataset {np.ndarray} -- Array of corresponding targets, of
                shape (#_training_data_points, ).
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        n_batches = np.floor(input_dataset.shape[0]/self.batch_size).astype(int)
        loss_arr = []
        for epoch in range(self.nb_epoch):

            if self.shuffle_flag:
                input_dataset,target_dataset = self.shuffle(input_dataset,target_dataset)

            data = np.hstack((input_dataset,target_dataset))
            batch_list = np.vsplit(data[:int(n_batches*self.batch_size)],n_batches)
            if int(n_batches*self.batch_size) != data.shape[0]:
                batch_list.append(data[int(n_batches*self.batch_size):])

            for batch in batch_list:
                loss = self.eval_loss(batch[:,:-target_dataset.shape[1]],batch[:,-target_dataset.shape[1]:])
                self.multilayer_network.backward(self.grad_z)
                self.multilayer_network.update_params(self.learning_rate)
                loss_arr.append(loss)
        return loss_arr
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def eval_loss(self, input_dataset, target_dataset):
        """
        Function that evaluate the loss function for given data.

        Arguments:
            - input_dataset {np.ndarray} -- Array of input features, of shape
                (#_evaluation_data_points, n_features).
            - target_dataset {np.ndarray} -- Array of corresponding targets, of
                shape (#_evaluation_data_points, ).
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        prediction = self.multilayer_network.forward(input_dataset)

        loss = self._loss_layer.forward(prediction, target_dataset)
        self.grad_z = self._loss_layer.backward()

        return loss
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


class Preprocessor(object):
    """
    Preprocessor: Object used to apply "preprocessing" operation to datasets.
    The object can also be used to revert the changes.
    """

    def __init__(self, data):
        """
        Initializes the Preprocessor according to the provided dataset.
        (Does not modify the dataset.)

        Arguments:
            - data {np.ndarray} dataset used to determined the parameters for
            the normalization. DATA HAS FEATURES - X
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        self.max_data = np.max(data, axis = 0)
        self.min_data = np.min(data, axis = 0)
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def apply(self, data):
        """
        Apply the pre-processing operations to the provided dataset.

        Arguments:
            - data {np.ndarray} dataset to be normalized.

        Returns:
            {np.ndarray} normalized dataset.
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        return (data - self.min_data)/(self.max_data - self.min_data)
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def revert(self, normalised_data):
        """
        Revert the pre-processing operations to retreive the original dataset.

        Arguments:
            - data {np.ndarray} dataset for which to revert normalization.

        Returns:
            {np.ndarray} reverted dataset.
        """
        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################
        return self.min_data + normalised_data*(self.max_data - self.min_data)
        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


def example_main():
    input_dim = 4
    neurons = [16, 3]
    activations = ["relu", "identity"]
    net = MultiLayerNetwork(input_dim, neurons, activations)

    dat = np.loadtxt("iris.dat")
    np.random.shuffle(dat)

    x = dat[:, :4]
    y = dat[:, 4:]

    split_idx = int(0.8 * len(x))

    x_train = x[:split_idx]
    y_train = y[:split_idx]
    x_val = x[split_idx:]
    y_val = y[split_idx:]

    prep_input = Preprocessor(x_train)

    x_train_pre = prep_input.apply(x_train)
    x_val_pre = prep_input.apply(x_val)

    trainer = Trainer(
        network=net,
        batch_size=8,
        nb_epoch=1000,
        learning_rate=0.01,
        loss_fun="softmax_cross_entropy",
        shuffle_flag=True,
    )

    trainer.train(x_train_pre, y_train)
    print("Train loss = ", trainer.eval_loss(x_train_pre, y_train))
    print("Validation loss = ", trainer.eval_loss(x_val_pre, y_val))

    preds = net(x_val_pre).argmax(axis=1).squeeze()
    targets = y_val.argmax(axis=1).squeeze()
    accuracy = (preds == targets).mean()
    print("Validation accuracy: {}".format(accuracy))


if __name__ == "__main__":
    example_main()
