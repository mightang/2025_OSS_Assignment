import numpy as np
import matplotlib.pyplot as plt

def read_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            if not line.startswith('#'):
                data.append([int(word) for word in line.split(',')])
    return data


if __name__ == '__main__':
    class_kr = read_data('data/class_score_kr.csv')
    class_en = read_data('data/class_score_en.csv')

    midterm_kr, final_kr = zip(*class_kr)
    total_kr = [40/125*mid + 60/100*fin for (mid, fin) in class_kr]

    midterm_en, final_en = zip(*class_en)
    total_en = [40/125*mid + 60/100*fin for (mid, fin) in class_en]

    data = np.vstack((class_kr, class_en))
    X = np.array(data)[:, 0]
    Y = np.array(data)[:, 1]

    A = np.vstack([X, np.ones(len(X))]).T
    line = np.linalg.pinv(A) @ Y
    a, b = line[0], line[1]

    print(f"Best-fit line: final = {a:.4f} * midterm + {b:.4f}\n")

    def predict(x):
        return a * x + b

    plt.figure(figsize=(8, 6))
    plt.scatter(midterm_kr, final_kr, color='blue', label='Korean Class', alpha=0.7)
    plt.scatter(midterm_en, final_en, color='red', label='English Class', alpha=0.7)
    x_range = np.array([0, 125])
    plt.plot(x_range, predict(x_range), 'g-', linewidth=2, label='Best-fit Line')
    plt.xlabel('Midterm Score (max 125)')
    plt.ylabel('Final Score (max 100)')
    plt.title('Midterm vs Final Exam Scores (with Line Fitting)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.figure(figsize=(8, 6))
    plt.hist(total_kr, bins=10, color='blue', alpha=0.6, label='Korean Class')
    plt.hist(total_en, bins=10, color='red', alpha=0.6, label='English Class')
    plt.xlabel('Total Score (weighted: 40% midterm + 60% final)')
    plt.ylabel('Number of Students')
    plt.title('Distribution of Total Scores')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.show()

    while True:
        midterm = float(input("Q) Please input your midterm score?"))
        predicted = predict(midterm)
        print(f"A) Your final score is expected to be {predicted:.3f}.\n")