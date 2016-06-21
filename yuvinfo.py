# coding: utf-8
__author__ = "ChenC"
try:
    from io import BytesIO as StringIO
except ImportError:
    from StringIO import StringIO


def parse_args():
    from argparse import ArgumentParser
    class EmptyArgumentError(Exception):
        pass
    parser = ArgumentParser(usage="python yuv.py -i file -s ???x??? -n ???")
    parser.add_argument("-i", "--input", help="输入的yuv序列")
    parser.add_argument("-s", "--size", help="图像宽高 默认是1280x720")
    parser.add_argument("-n", "--number", help="第几帧")
    args = parser.parse_args()
    if args.input is None:
        raise EmptyArgumentError("需要输入文件")
    if args.size is None:
        args.size = "1280x720"
    if args.number is not None:
        args.number = int(args.number)
    w, h = map(lambda t: int(t) , args.size.split("x"))
    return args.number, args.input, w, h


class YUV(object):


    def __init__(self, input, width, height):
        self.input = input
        self.width, self.height = width, height
        self.quater = self.width * self.height // 4
        self.buffer = StringIO()
        self._init()

    def _init(self):
        with open(self.input, "rb") as fp:
            self.buffer.write(fp.read())
        self.refresh()

    yuv2rgb = lambda self, yuv: [[int(c[0] + 1.4075 * c[2]),
                                  int(c[0] - 0.3455 * c[1] - 0.7196 * c[2]),
                                  int(c[0] + 1.7790 * c[1])] for c in yuv]

    def refresh(self):
        self.buffer.seek(0)

    def catch(self, sequence):
        self.buffer.seek((sequence-1)*self.quater*6)
        data = self.buffer.read(self.quater*6)
        self.refresh()
        yuv = self.load(data)
        rgb = self.yuv2rgb(yuv)
        for i in range(len(rgb)):
            for j in range(3):
                rgb[i][j] = \
                255 if rgb[i][j] > 255 else 0 if rgb[i][j] < 0 else rgb[i][j]
        return rgb

    def load(self, data):
        yuv = []
        cy = data[:self.quater*4 ]
        cu = data[self.quater*4 : self.quater*5]
        cv = data[self.quater*5 : self.quater*6]
        for i in range(self.quater * 4):
            row = i // (width * 2)
            col = (i % width) // 2
            index = int(row * width / 2 + col)
            yuv.append([
                        cy[i],
                        cu[index] - 128,
                        cv[index] - 128
                        ])
        return yuv

    def frames(self):
        from os.path import getsize
        return getsize(input) // (self.quater * 6)

    def show(self, sequence):
        from PIL import Image
        from struct import pack
        tbuffer = StringIO()
        rgb = self.catch(sequence)
        for c in rgb:
            tbuffer.write(pack("BBB", c[0], c[1], c[2]))
        Image.frombuffer("RGB", (self.width, self.height), tbuffer.getvalue(), "raw", "RGB", 0, 1).show()
        exit(0)

    def __del__(self):
        self.buffer.close()


if __name__ == "__main__":
    number, input, width, height = parse_args()
    yuv = YUV(input, width, height)
    if number is None:
        print("图片有: ", yuv.frames(), "帧")
    else:
        yuv.show(number)
