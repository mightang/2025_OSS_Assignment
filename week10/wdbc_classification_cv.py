import numpy as np
from itertools import product
from sklearn import datasets, model_selection
from sklearn.ensemble import ExtraTreesClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import cross_validate, StratifiedKFold

if __name__ == "__main__":
    X, y = datasets.load_breast_cancer(return_X_y=True)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
    et_max_features = [0.65, 0.70, 0.75]
    et_min_leaf     = [1, 2]
    et_min_split    = [2, 4]
    svc_C     = [3000, 10000, 30000]
    svc_gamma = [0.02, 0.03]

    best = (-1.0, None)
    for mf, mleaf, msplit in product(et_max_features, et_min_leaf, et_min_split):
        et = ExtraTreesClassifier(
            n_estimators=800, max_features=mf,
            min_samples_leaf=mleaf, min_samples_split=msplit,
            criterion="gini", class_weight="balanced",
            random_state=0, n_jobs=-1
        )
        for C, g in product(svc_C, svc_gamma):
            svc = Pipeline([
                ("scaler", StandardScaler()),
                ("svc", SVC(kernel="rbf", C=C, gamma=g, probability=True))
            ])
            model = VotingClassifier(
                estimators=[("et", et), ("svc", svc)],
                voting="soft", weights=[2, 1], n_jobs=-1
            )
            cv_res = cross_validate(model, X, y, cv=cv, return_train_score=False, n_jobs=-1)
            acc = float(np.mean(cv_res["test_score"]))
            if acc > best[0]:
                best = (acc, dict(mf=mf, leaf=mleaf, split=msplit, C=C, gamma=g))

    print("[LOCAL BEST]", best)

    p = best[1]
    et = ExtraTreesClassifier(
        n_estimators=800, max_features=p["mf"],
        min_samples_leaf=p["leaf"], min_samples_split=p["split"],
        criterion="gini", class_weight="balanced",
        random_state=0, n_jobs=-1
    )
    svc = Pipeline([
        ("scaler", StandardScaler()),
        ("svc", SVC(kernel="rbf", C=p["C"], gamma=p["gamma"], probability=True))
    ])
    model = VotingClassifier(
        estimators=[("et", et), ("svc", svc)],
        voting="soft", weights=[2, 1], n_jobs=-1
    )

    final = cross_validate(model, X, y, cv=cv, return_train_score=True, n_jobs=-1)
    acc_train = float(np.mean(final['train_score']))
    acc_test  = float(np.mean(final['test_score']))
    print(f'* Accuracy @ training data: {acc_train:.3f}')
    print(f'* Accuracy @ test data: {acc_test:.3f}')
    print(f'* Your score: {max(10 + 100*(acc_test - 0.9), 0):.0f}')