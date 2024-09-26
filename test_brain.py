from brain.brain import solver, load_data


if __name__ == '__main__':
    train = True
    path = f'../ARC-AGI/data/{"training" if train else "evaluation"}'
    data = load_data(path)

    correct_cnt = 0
    failure_cnt = 0
    for k, v in data.items():
        f = solver(v, k=k)
        if f is not None:
            success = True
            for test_case in v.train + v.test:
                if f(test_case.input) != test_case.output:
                    print(f"Failed on {k}")
                    print("expected:")
                    print(test_case.output)
                    print("got:")
                    print(f(test_case.input))
                    failure_cnt += 1
                    success = False
                    break
            if success:
                print(f"{k} solved")
                correct_cnt += 1
    print(f"Failures: {failure_cnt} / {failure_cnt + correct_cnt}")
    print(f"Accuracy: {correct_cnt} / {len(data)}")

