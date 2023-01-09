# ======================================================================================================================
import marshal
import dis
import sys
from datetime import datetime

# ======================================================================================================================
PYTHON_MAGIC = {
    # https://github.com/google/pytype/blob/main/pytype/pyc/magic.py
    # https://stackoverflow.com/questions/7807541/is-there-a-way-to-know-by-which-python-version-the-pyc-file-was-compiled

    # Python 1
    20121: (1, 5),
    50428: (1, 6),

    # Python 2
    50823: (2, 0),
    60202: (2, 1),
    60717: (2, 2),
    62011: (2, 3),  # a0
    62021: (2, 3),  # a0
    62041: (2, 4),  # a0
    62051: (2, 4),  # a3
    62061: (2, 4),  # b1
    62071: (2, 5),  # a0
    62081: (2, 5),  # a0
    62091: (2, 5),  # a0
    62092: (2, 5),  # a0
    62101: (2, 5),  # b3
    62111: (2, 5),  # b3
    62121: (2, 5),  # c1
    62131: (2, 5),  # c2
    62151: (2, 6),  # a0
    62161: (2, 6),  # a1
    62171: (2, 7),  # a0
    62181: (2, 7),  # a0
    62191: (2, 7),  # a0
    62201: (2, 7),  # a0
    62211: (2, 7),  # a0

    # Python 3
    3000: (3, 0),
    3010: (3, 0),
    3020: (3, 0),
    3030: (3, 0),
    3040: (3, 0),
    3050: (3, 0),
    3060: (3, 0),
    3061: (3, 0),
    3071: (3, 0),
    3081: (3, 0),
    3091: (3, 0),
    3101: (3, 0),
    3103: (3, 0),
    3111: (3, 0),  # a4
    3131: (3, 0),  # a5

    # Python 3.1
    3141: (3, 1),  # a0
    3151: (3, 1),  # a0

    # Python 3.2
    3160: (3, 2),  # a0
    3170: (3, 2),  # a1
    3180: (3, 2),  # a2

    # Python 3.3
    3190: (3, 3),  # a0
    3200: (3, 3),  # a0
    3220: (3, 3),  # a1
    3230: (3, 3),  # a4

    # Python 3.4
    3250: (3, 4),  # a1
    3260: (3, 4),  # a1
    3270: (3, 4),  # a1
    3280: (3, 4),  # a1
    3290: (3, 4),  # a4
    3300: (3, 4),  # a4
    3310: (3, 4),  # rc2

    # Python 3.5
    3320: (3, 5),  # a0
    3330: (3, 5),  # b1
    3340: (3, 5),  # b2
    3350: (3, 5),  # b2
    3351: (3, 5),  # 3.5.2

    # Python 3.6
    3360: (3, 6),  # a0
    3361: (3, 6),  # a0
    3370: (3, 6),  # a1
    3371: (3, 6),  # a1
    3372: (3, 6),  # a1
    3373: (3, 6),  # b1
    3375: (3, 6),  # b1
    3376: (3, 6),  # b1
    3377: (3, 6),  # b1
    3378: (3, 6),  # b2
    3379: (3, 6),  # rc1

    # Python 3.7
    3390: (3, 7),  # a1
    3391: (3, 7),  # a2
    3392: (3, 7),  # a4
    3393: (3, 7),  # b1
    3394: (3, 7),  # b5

    # Python 3.8
    3400: (3, 8),  # a1
    3401: (3, 8),  # a1
    3410: (3, 8),  # a1
    3411: (3, 8),  # b2
    3412: (3, 8),  # b2
    3413: (3, 8),  # b4

    # Python 3.9
    3420: (3, 9),  # a0
    3421: (3, 9),  # a0
    3422: (3, 9),  # a0
    3423: (3, 9),  # a2
    3424: (3, 9),  # a2
    3425: (3, 9),  # a2

    # Python 3.10
    3430: (3, 10),  # a1
    3431: (3, 10),  # a1
    3432: (3, 10),  # a2
    3433: (3, 10),  # a2
    3434: (3, 10),  # a6
    3435: (3, 10),  # a7
    3436: (3, 10),  # b1
    3437: (3, 10),  # b1
    3438: (3, 10),  # b1
    3439: (3, 10),  # b1
}

# ======================================================================================================================
def show_code(filepath):
    """
        https://stackoverflow.com/a/32562303

        header_sizes = [
                # (size, first version this applies to)

                (8,  (0, 9, 2)),  # 2 bytes magic number, \r\n, 4 bytes UNIX timestamp

                (12, (3, 6)),     # added 4 bytes file size
                # bytes 4-8 are flags, meaning of 9-16 depends on what flags are set
                # bit 0 not set: 9-12 timestamp, 13-16 file size
                # bit 0 set: 9-16 file hash (SipHash-2-4, k0 = 4 bytes of the file, k1 = 0)

                (16, (3, 7)),     # inserted 4 bytes bit flag field at 4-8
                # future version may add more bytes still, at which point we can extend

                # this table. It is correct for Python versions up to 3.9
            ]
    :param filepath:
    :return:
    """

    header_sizes = [
        (8,  (0, 9, 2)),
        (12, (3, 6)),
        (16, (3, 7)),
    ]
    header_size = next(s for s, v in reversed(header_sizes) if sys.version_info >= v)

    with open(filepath, "rb") as f:
        pyc_version    = PYTHON_MAGIC.get( int.from_bytes(f.read(4)[:2], 'little') )
        python_version = (sys.version_info.major, sys.version_info.minor)

        if not (pyc_version[0] == python_version[0] and pyc_version[1] == python_version[1]):
            print(f"You are using Python {python_version[0]}.{python_version[1]}. Please, use the same version of .pyc: Python {pyc_version[0]}.{pyc_version[1]}")
            return

        metadata = f.read(header_size - 4)      # first header_size bytes are metadata
        code     = marshal.load(f)              # rest is a marshalled code object

    now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    with open(f'{now}.txt', 'w') as sys.stdout:
        dis.dis(code)

# ======================================================================================================================
if __name__ == "__main__":
    path = sys.argv[1]
    show_code(path)
