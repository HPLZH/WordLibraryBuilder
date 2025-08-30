from typing import Iterable
import os
import re
import json


def ls(path: str, exclude: None | Iterable[str] = None) -> tuple[str] | list[str]:
    assert os.path.exists(path)
    if os.path.isfile(path):
        return (path,)
    elif os.path.isdir(path):
        r = []
        for s in os.listdir(path):
            t = os.path.join(path, s)
            for ex in exclude if exclude else []:
                if os.path.commonpath((ex, t)) == ex:
                    break
            else:
                r += ls(t, exclude)
        return r
    else:
        return []


class TargetInfo:
    src: list[str]
    tags: list[str]
    exclude: list[str]
    f_include: list[re.Pattern]
    f_exclude: list[re.Pattern]

    def __init__(self, json: dict) -> None:
        assert "src" in json
        if isinstance(json["src"], str):
            self.src = [os.path.abspath(json["src"])]
        else:
            self.src = [os.path.abspath(p) for p in json["src"]]

        assert "tags" in json
        if isinstance(json["tags"], str):
            assert json["tags"] == "any"
            self.tags = []
        else:
            self.tags = list(json["tags"])

        if "exclude" in json:
            self.exclude = [os.path.abspath(p) for p in json["exclude"]]
        else:
            self.exclude = []

        self.f_exclude = []
        self.f_include = []
        if "filter" in json:
            jf = json["filter"]
            if "include" in jf:
                self.f_include = [re.compile(p) for p in jf["include"]]
            if "exclude" in jf:
                self.f_include = [re.compile(p) for p in jf["exclude"]]

    def ls(self) -> list[str]:
        r = []
        f_i = self.f_include
        f_e = self.f_exclude
        for l in self.src:
            r += ls(l, self.exclude)
        print(r)
        r1 = filter(lambda x: any(rx.search(x) != None for rx in f_i), r) if len(f_i) else r
        print(list(r1))
        r2 = filter(lambda x: not any(rx.search(x) != None for rx in f_e), r1)
        return list(r2)

    def build(self) -> Iterable[str]:
        r = set()
        for fn in self.ls():
            with open(fn, "r", encoding="utf-8") as f:
                o = json.load(f)
                for k in o:
                    if len(self.tags) == 0 or k in self.tags:
                        r.update(list(o[k]))
        return r


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str, help="配置文件")
    parser.add_argument("output", type=str, help="输出目标文件")
    parser.add_argument(
        "-d", type=str, dest="dep", help="改为输出依赖文件，而不是目标文件"
    )

    args = parser.parse_args()

    target = args.config
    output = args.output
    dep = args.dep

    with open(target, "r", encoding="utf-8") as f:
        o = json.load(f)
    t = TargetInfo(o)

    if dep:
        l = [os.path.relpath(p).replace("\\", "/") for p in sorted(t.ls())]
        with open(dep, "w", encoding="utf-8") as f:
            f.write(f"{output} : {target} {" ".join(l)}")
    else:
        r = t.build()
        with open(output, "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in r)
