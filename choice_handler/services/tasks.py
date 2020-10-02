from __future__ import absolute_import, unicode_literals
import random
from celery import shared_task
import redis


@shared_task(name="sum_two_numbers")
def add(x, y):
    return x + y


@shared_task(name="multiply_two_numbers")
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total


@shared_task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)


if __name__ == '__main__':
    # Redis<ConnectionPool<Connection>>
    r = redis.Redis(host="host.docker.internal", port=6379,
                    decode_responses=True)

    print(r.ping())  # // True
    print(r.set(name="야", value="호"))  # // True
    print(r.get(name="야"))  # // 호
