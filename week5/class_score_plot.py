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
    total_kr = [40/125*midterm + 60/100*final for (midterm, final) in class_kr]

    midterm_en, final_en = zip(*class_en)
    total_en = [40/125*midterm + 60/100*final for (midterm, final) in class_en]

    plt.figure(figsize=(8, 6))
    plt.scatter(midterm_kr, final_kr, label='Korean Class')
    plt.scatter(midterm_en, final_en, label='English Class')
    plt.xlabel('Midterm Score (max 125)')
    plt.ylabel('Final Score (max 100)')
    plt.xlim(0, 125)
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    plt.title('Midterm vs Final Scores')
    plt.savefig('class_score_scatter.png')
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.hist(total_kr, bins=range(0, 105, 5), alpha=0.7, label='Korean Class')
    plt.hist(total_en, bins=range(0, 105, 5), alpha=0.7, label='English Class')
    plt.xlabel('Total Score')
    plt.ylabel('Number of Students')
    plt.xlim(0, 100)
    plt.legend()
    plt.title('Distribution of Total Scores')
    plt.savefig('class_score_hist.png')
    plt.show()