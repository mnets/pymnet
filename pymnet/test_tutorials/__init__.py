from .tutorial_test import test_tutorials

def test_all():
    codes = []
    codes.append(test_tutorials())
    return all(codes)
