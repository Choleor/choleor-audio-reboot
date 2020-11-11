
def listdict_to_dictlist(_dict, op="compact"):
    """
    리스트를 value로 갖고 있는 딕셔너리 계층구조
     -> 딕셔너리들의 리스트로 바꾸는 함수
    """
    if op not in ("compact", "extended"):
        raise Exception("No such an option")

    max_len = max([len(v) for v in _dict.values()])
    return ([{k: _dict[k][i] for k in _dict.keys() if i < len(_dict[k])} for i in
             range(max_len)] if op != "extended" else [
        {k: (_dict[k][i] if i < len(_dict[k]) else "") for k in _dict.keys()} for i in range(max_len)])


def dictlist_to_listdict(_list):
    """
    딕셔너리들이 원소인 리스트
     -> 각 딕셔너리(원소)에 존재하는 키에 대한 value 리스트로 구성되어있는 딕셔너리
    """
    keyset = {}
    for d in _list:
        keyset = {*keyset, *d}
    # dictionary comprehension -> make res
    ret = {k: [dicit.get(k) for dicit in _list if bool(dicit.get(k))] for k in keyset}
    print(ret)
    return ret
