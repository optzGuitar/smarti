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
            b"\x80\x04\x95\x0b\x00\x00\x00\x00\x00\x00\x00]\x94(K\x01K\x02K\x03e.",
        ),
        b"\x80\x04\x95#\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01a\x94\x8c\x01x\x94\x8c\x08f_kwargs\x94}\x94h\x02\x8c\x03bla\x94su.",
    )
    storage = InstanceStorage()

    generated = storage._generate_key(
        "a", "B", Testclass, [1, 2, 3], {"a": "x", "f_kwargs": {"x": "bla"}}
    )

    assert expected == generated
