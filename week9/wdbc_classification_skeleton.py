import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn import(datasets, metrics)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

def load_wdbc_data(filename):
    class WDBCData:
        data          = [] # Shape: (569, 30)
        target        = [] # Shape: (569, )
        target_names  = ['malignant', 'benign']
        feature_names = ['mean radius', 'mean texture', 'mean perimeter', 'mean area', 'mean smoothness', 'mean compactness', 'mean concavity', 'mean concave points', 'mean symmetry', 'mean fractal dimension',
                         'radius error', 'texture error', 'perimeter error', 'area error', 'smoothness error', 'compactness error', 'concavity error', 'concave points error', 'symmetry error', 'fractal dimension error',
                         'worst radius', 'worst texture', 'worst perimeter', 'worst area', 'worst smoothness', 'worst compactness', 'worst concavity', 'worst concave points', 'worst symmetry', 'worst fractal dimension']
    wdbc = WDBCData()
    with open(filename) as f:
        for line in f.readlines():
            items = line.split(',')
            wdbc.target.append(0 if items[1] == 'M' else 1)
            wdbc.data.append([float(x) for x in items[2:32]])
        wdbc.data = np.array(wdbc.data, dtype=float)
        wdbc.target = np.array(wdbc.target, dtype=int)
    return wdbc

if __name__ == '__main__':
    # Load a dataset
    wdbc = load_wdbc_data('data/wdbc.data')

    # Train a model
    model = RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42, n_jobs = -1)
    model.fit(wdbc.data, wdbc.target)

    # Test the model
    predict = model.predict(wdbc.data)
    accuracy = metrics.balanced_accuracy_score(wdbc.target, predict)

    # Visualize testing results
    cmap = np.array([(1, 0, 0), (0, 1, 0)])
    clabel = [Line2D([0], [0], marker='o', lw=0, label=wdbc.target_names[i], color=cmap[i]) for i in range(len(cmap))]
    for (x, y) in [(0, 1)]: # Not mandatory, but try [(i, i+1) for i in range(0, 30, 2)]
        plt.figure()
        plt.title(f'My Classifier (Accuracy: {accuracy:.3f})')
        plt.scatter(wdbc.data[:,x], wdbc.data[:,y], c=cmap[wdbc.target], edgecolors=cmap[predict])
        plt.xlabel(wdbc.feature_names[x])
        plt.ylabel(wdbc.feature_names[y])
        plt.legend(handles=clabel, framealpha=0.5)

    cm = confusion_matrix(wdbc.target, predict, labels=[0, 1])
    class_names = wdbc.target_names  # ['malignant','benign']

    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap='viridis')

    cbar = fig.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(len(class_names)),
        yticks=np.arange(len(class_names)),
        xticklabels=class_names,
        yticklabels=class_names,
        xlabel='Predicted label',
        ylabel='True label',
        title=f'Confusion Matrix (Balanced Acc: {accuracy:.3f})'
    )

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, f'{cm[i, j]:d}',
                ha='center', va='center',
                color=('yellow' if cm[i, j] > thresh else 'white'),
                fontsize=12
            )

    fig.tight_layout()

    plt.show()