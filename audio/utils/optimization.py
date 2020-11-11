from multiprocessing import Process


def single_process_to_multi_process(iter_number, thread_number, iterative_func):
    _disperser = [1] * (iter_number % thread_number) + [0] * (thread_number - iter_number % thread_number)
    start = [i * (iter_number // thread_number) + _disperser.pop() for i in range(thread_number)]
    process_lists = list(
        map(lambda x, y: Process(target=iterative_func, args=(x, y)), start, start[1:] + [iter_number - 1]))

    for process in process_lists:
        process.start()
    for process in process_lists:
        process.join()
