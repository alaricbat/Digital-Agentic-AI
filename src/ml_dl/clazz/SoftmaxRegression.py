import numpy as np

class SoftmaxRegression:

    def __init__(self,
                 lamda = 0.5,
                 epoches = 100,
                 batch_size = 10,
                 learning_rate = 0.05):
        self.w = None
        self.lamda = lamda
        self.epoches = epoches
        self.batch_size = batch_size
        self.learning_rate = learning_rate

    def fit(self, X, y, C):

        X = np.array(X)
        y = np.array(y, dtype=np.int64)

        y_one_hot = np.eye(C)[y].astype(int)

        N = X.shape[0]
        self.w = np.random.rand(X.shape[1], y_one_hot.shape[1])
        w_old = self.w.copy()

        class_counts = np.bincount(y, minlength=C)
        class_counts = np.where(class_counts == 0, 1, class_counts)
        class_weights = N / (C * class_counts) 

        hist_loss = []

        for _ in range(self.epoches):

            mix_ids = np.random.permutation(N)
            num_batches = int(np.ceil(N / self.batch_size))

            for batch in range(num_batches):

                batch_ids = mix_ids[batch * self.batch_size : min(self.batch_size * (batch + 1), N)]
                X_batch = X[batch_ids]
                y_batch = y_one_hot[batch_ids]

                y_batch_labels = y[batch_ids]
                batch_weights = class_weights[y_batch_labels].reshape(-1, 1)

                a = self.__softmax(X_batch @ self.w)

                err = (a - y_batch) * batch_weights
                gradient = (X_batch.T @ err + self.lamda * self.w) / X_batch.shape[0]
                self.w -= self.learning_rate * gradient
            hist_loss.append(self.loss(X, y_one_hot))
            if np.linalg.norm(self.w - w_old) / self.w.size < 1e-5:
                break
            w_old = self.w.copy() 
        return hist_loss, self.w

    def loss(self, X, y):
        A = self.__softmax(X @ self.w)
        A = np.clip(A, 1e-15, 1.0 - 1e-15)
        core_loss = -np.sum(y * np.log(A)) / X.shape[0]
        reg_loss = 0.5 * self.lamda * np.sum(self.w ** 2) / X.shape[0]
        return core_loss + reg_loss


    def predict(self, X):
        X = np.array(X)
        probs = self.__softmax(X @ self.w)
        return np.argmax(probs, axis=1)

    def __softmax(self, Z):
        '''
        Compute softmax values for eache sets of scores in Z.
        each row of Z is a set of scores.
        '''
        e_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
        A = e_Z / e_Z.sum(axis=1, keepdims=True)
        return A