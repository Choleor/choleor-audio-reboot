from multiprocessing import Process


def single_process_to_multi_process(iter_number, thread_number, iterative_func):
    """
    for loop 등의 순차처리할 대상을 바꿔 multi-processing을 적용할 수 있도록 해주는
    :param iter_number:
    :param thread_number: 총 iteration 횟수
    :param iterative_func:
    :return:
    """
    _disperser = [1] * (iter_number % thread_number) + [0] * (thread_number - iter_number % thread_number)
    start = [i * (iter_number // thread_number) + _disperser.pop() for i in range(thread_number)]
    end = start[1:] + [iter_number - 1]
    process_lists = list(
        map(lambda x, y: Process(target=iterative_func, args=(x, y)), start, end))

    for process in process_lists:
        process.start()
    for process in process_lists:
        process.join()
