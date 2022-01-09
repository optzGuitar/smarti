from smarti.instance_storage import InstanceStorage


class Testclass:
    pass


def test_add_instance():
    storage = InstanceStorage()

    args = ["bla"]
    instance = Testclass()

    storage.add_or_get(Testclass, instance, args, {"a": "b"})
    key = storage._generate_key(
        "tests.test_instance_storage", "Testclass", Testclass, args, {"a": "b"}
    )
    assert storage._storage[key] == instance

    storage.add_or_get(Testclass, instance, args, {"a": "b"})
    assert len(storage._storage) == 1


def test_get_instance():
    storage = InstanceStorage()

    args = ["bla"]
    instance = Testclass()

    key = storage._generate_key(
        "tests.test_instance_storage", "Testclass", Testclass, args, {"a": "b"}
    )
    storage._storage[key] = instance

    stored = storage.get_instance(Testclass, args, {"a": "b"})

    assert stored is instance

    stored2 = storage.get_instance(Testclass, args, {"a": "b"})
    assert stored2 is stored is instance


def test_generate_key():
    expected = (
        "a.B",
        (
            "args",
            b"\x80\x04\x95/\x00\x00\x00\x00\x00\x00\x00]\x94C(\x80\x04\x95\x1d\x00\x00\x00\x00\x00\x00\x00]\x94(C\x05\x80\x04K\x01.\x94C\x05\x80\x04K\x02.\x94C\x05\x80\x04K\x03.\x94e.\x94a.",
        ),
        b"\x80\x04\x95\x85\x00\x00\x00\x00\x00\x00\x00]\x94(C\x10\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00\x8c\x01a\x94.\x94C\x10\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00\x8c\x01x\x94.\x94\x86\x94C\x17\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00\x8c\x08f_kwargs\x94.\x94C9\x80\x04\x95.\x00\x00\x00\x00\x00\x00\x00]\x94C\x10\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00\x8c\x01x\x94.\x94C\x12\x80\x04\x95\x07\x00\x00\x00\x00\x00\x00\x00\x8c\x03bla\x94.\x94\x86\x94a.\x94\x86\x94e.",
    )
    storage = InstanceStorage()

    generated = storage._generate_key(
        "a", "B", Testclass, [1, 2, 3], {"a": "x", "f_kwargs": {"x": "bla"}}
    )

    assert expected == generated
