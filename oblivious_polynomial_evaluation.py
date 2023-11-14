from typing import Callable

import numpy as np


class Sender:
    def __init__(self, degree: int, alpha: float, dp: int = 1) -> None:
        self.degree = degree
        self.dp = dp
        self.alpha = alpha
        self.P = self.generate_polynomial(degree * dp, alpha)
        self.Px = self.generate_polynomial(degree)

    @staticmethod
    def generate_polynomial(degree: int, alpha: float = 0) -> np.poly1d:
        coeffs = np.random.rand(degree + 1)
        coeffs[0] = alpha  # Set the constant term to alpha
        return np.poly1d(coeffs[::-1])

    def create_bivariate_polynomial(self) -> Callable[[float, float], float]:
        def Q(x: float, y: float) -> float:
            return self.Px(x) + self.P(y)

        return Q


class Receiver:
    def __init__(self, degree: int, alpha: float, N: int) -> None:
        self.degree = degree
        self.alpha = alpha
        self.N = N
        self.S = self.generate_polynomial(degree, alpha)
        self.x_values = np.random.choice(np.linspace(0, 1, 1000), N, replace=False)
        self.T = np.sort(np.random.choice(range(N), degree + 1, replace=False))
        self.y_values = np.array([
            self.S(self.x_values[i]) if i in self.T else np.random.rand()
            for i in range(N)
        ])

    @staticmethod
    def generate_polynomial(degree: int, alpha: float = 0) -> np.poly1d:
        coeffs = np.random.rand(degree + 1)
        coeffs[0] = alpha
        return np.poly1d(coeffs[::-1])

    def create_univariate_polynomial(self, Q: Callable[[float, float], float]) -> Callable[[float], float]:
        def R(x: float) -> float:
            return Q(x, self.S(x))

        return R

    @staticmethod
    def evaluate_polynomial(poly: np.poly1d, points: np.ndarray) -> np.ndarray:
        return np.array([poly(point) for point in points])

    def perform_oblivious_transfer(self, R: Callable[[float], float]) -> np.ndarray:
        # This is a simplified version of the oblivious transfer
        return self.evaluate_polynomial(R, self.x_values[self.T])

    @staticmethod
    def interpolate_polynomial(R: Callable[[float], float]) -> float:
        # In practice, more sophisticated methods would be used
        return R(0)


if __name__ == "__main__":
    # Example usage:
    k = 3  # Degree of the polynomial
    dp = 10
    alpha = np.random.rand()  # Choose a random alpha
    N = k * dp  # N = nm (for simplicity)

    # Initialize sender and receiver
    sender = Sender(k, alpha, 10)
    receiver = Receiver(k, alpha, N)

    # Sender creates bivariate polynomial
    Q = sender.create_bivariate_polynomial()

    # Receiver creates univariate polynomial
    R = receiver.create_univariate_polynomial(Q)

    # Oblivious transfer
    oblivious_transfer_values = receiver.perform_oblivious_transfer(R)

    # Receiver interpolates polynomial to find P(alpha)
    learned_P_alpha = receiver.interpolate_polynomial(R)

    print(f"Original P(alpha): {sender.P(alpha)}")
    print(f"Learned P(alpha): {learned_P_alpha}")
    print(
        f"Are the original and learned P(alpha) equal? {'Yes' if np.isclose(sender.P(alpha), learned_P_alpha) else 'No'}")
