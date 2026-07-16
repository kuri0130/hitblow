"""core.judge のテスト（最初から緑）。機能を足しても緑を保とう＝回帰テスト。"""

from hitblow.core import judge


def test_all_hit():
    assert judge("123", "123") == (3, 0)


def test_all_blow():
    assert judge("123", "231") == (0, 3)


def test_mix():
    assert judge("123", "132") == (1, 2)


def test_none():
    assert judge("123", "456") == (0, 0)
