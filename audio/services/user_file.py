import asyncio
import time
from audio.utils.utils import get_console_output


def get_duration(filename, ext, in_path):
    return float(get_console_output(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}/{}.{}".format(
            in_path, filename, ext)))


async def example():
    print(f"started at {time.strftime('%X')}")
    # task4 = asyncio.create_task(temp(1000000))
    # task1 = asyncio.create_task(aggregate(190, 0.5, 0.2, 23232, 546, 7, 77, 8, 89))
    # task5 = asyncio.create_task(temp(10))
    # task2 = asyncio.create_task(
    #     aggregate(10, 20, 30, 1111, 2, 303030, 23, 43, 4, 4, 6, 78, 8, 12, 3, 47, 12, 5423, 513, 0.1235, 3939))
    # task3 = asyncio.create_task(aggregate(10000, 2022, 303))
    await asyncio.gather(
        temp(1000003232),
        temp(3999423),
        aggregate(1, 5, 7, 9, 6, 4, 32, 3, 4.9, -194956.585, 198, 238, 384, 7607, 29394000),
        temp(2444672),
        temp(2),
        aggregate(2)
    )
    print(f"finished at {time.strftime('%X')}")
    # await aggregate(190, 0.5, 0.2)
    # await aggregate(10, 20, 30, 1111, 2, 303030)
    # await print("hello")


async def ex2(delay, what):
    print(f"ex2started at {time.strftime('%X')}")
    await asyncio.sleep(delay)
    print(what)
    print(f"ex2 finished at {time.strftime('%X')}")


async def temp(input):
    print("temp: " + str(input) + " comes")
    await asyncio.sleep(0.01)
    sum = 0
    for i in range(input):
        sum += i * 3
    print("(temp function result) sum is " + str(sum))
    return sum


async def aggregate(*args):
    print(args)
    await asyncio.sleep(0.01)
    sum = 0
    for i in args:
        sum += i
    print("aggregate function result is " + str(sum))
    return sum


if __name__ == '__main__':
    # print(get_duration("J3d5OkPxER4", "wav", "../../media"))
    asyncio.run(example())
